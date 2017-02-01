import numpy as np
import cv2
import argparse
import time, sys, os, signal
import mqttClient
import json

from GameTarget import GameTarget
from RealtimeInterval import RealtimeInterval
from CVParameterGroup import CVParameterGroup
import TriangleSimilarityDistanceCalculator as DistanceCalculator
import CameraReaderAsync
from WeightedFramerateCounter import WeightedFramerateCounter

''' hunt.py
	Computer vision main module for Rex Machina 2017 competition
'''

MQTT_TOPIC_TARGETING = "rex/vision/telemetry"
MQTT_TOPIC_SCREENSHOT = "rex/vision/screenshot"
MQTT_TOPIC_SHUTDOWN = "res/robot/disabled"
MQTT_HOST = "roboRIO-5495-FRC.local"
MQTT_HOST_DEBUG = "10.0.1.94"
MQTT_PORT = 5888

# Tunable parameters
REFERENCE_BOILER_WIDTH = 100
REFERENCE_LIFT_HEIGHT = 100

g_debugMode = True
g_cameraFrameWidth = 0
g_cameraFrameHeight = 0
g_testImage = None
g_shutdown = False

class Killer:
    dienow = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.dienow = True

def printif(message):
    if g_debugMode:
        print message

def messageHandler(message):
    sys.stdout.write(".")
    if message.topic == MQTT_TOPIC_SHUTDOWN:
        g_shutdown = True

def setCVParameters(params):
    # HUES: GREEEN=65/75 BLUE=110
    params.addParameter("hue", 75, 179)
    params.addParameter("hueWidth", 20, 25)
    params.addParameter("low", 70, 255)
    params.addParameter("high", 255, 255)
    params.addParameter("countourSize", 50, 200)
    params.addParameter("keystone", 0, 320)

def createCamera():
    # return a camera object with exposure and contrast set
    global g_cameraFrameWidth
    global g_cameraFrameHeight

    camera = cv2.VideoCapture(0)
    # No camera's exposure goes this low, but this will set it as low as possible
    # camera.set(cv2.cv.CV_CAP_PROP_EXPOSURE,-100)
    # camera.set(cv2.cv.CV_CAP_PROP_FPS, 15)
    # camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    # camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
    g_cameraFrameWidth = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    g_cameraFrameHeight = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return camera

def filterHue(source, hue, hueWidth, low, high):
    MAX_HUE = 179
    hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)

    lowHue = max(hue - hueWidth, 0)
    lowFilter = np.array([lowHue, low, low])

    highHue = min(hue + hueWidth, MAX_HUE)
    highFilter = np.array([highHue, high, high])

    return cv2.inRange(hsv, lowFilter, highFilter)

def findTargetPair(raw, params):
    global g_debugMode
    mask = filterHue(raw, params["hue"], params["hueWidth"], params["low"], params["high"])
    if g_debugMode:
        cv2.imshow("mask", mask)
    __, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        largestContours = sorted(contours, key = cv2.contourArea, reverse = True)[:2]
        if cv2.contourArea(largestContours[0]) > params["countourSize"] \
                and cv2.contourArea(largestContours[1]) > params["countourSize"]:
            return largestContours

def main():
    killer = Killer()
    params = CVParameterGroup("Sliders", g_debugMode)
    setCVParameters(params)

    connectThrottle = RealtimeInterval(10)
    topics = [MQTT_TOPIC_SCREENSHOT, MQTT_TOPIC_SHUTDOWN]
    if g_debugMode:
        host = MQTT_HOST_DEBUG
    else:
        host = MQTT_HOST
    client = mqttClient.MqttClient(host, MQTT_PORT, topics, messageHandler)

    # Start the camera
    camera = cameraReader = None
    if g_testImage is None:
        camera = createCamera()
        cameraReader = CameraReaderAsync.CameraReaderAsync(camera)

    gameTarget = GameTarget(g_debugMode)

    fpsDisplay = True
    fpsCounter = WeightedFramerateCounter()
    fpsInterval = RealtimeInterval(5.0, False)

    # The first frame we take off of the camera won't have the proper exposure setting
    # We need to skip the first frame to make sure we don't process bad image data.
    firstFrameSkipped = False

    boilerDistance = DistanceCalculator.TriangleSimilarityDistanceCalculator(REFERENCE_BOILER_WIDTH,
                                                                                  DistanceCalculator.PFL_H_C920)
    liftDistance = DistanceCalculator.TriangleSimilarityDistanceCalculator(REFERENCE_LIFT_HEIGHT,
                                                                                  DistanceCalculator.PFL_V_C920)

    # Loop on acquisition
    while not g_shutdown and not killer.dienow:
        if (not client.isConnected()) and connectThrottle.hasElapsed():
            try:
                client.connect()
            except:
                None
        raw = None
        if g_testImage is not None:
            # Use a file image if provided, for testing
            raw = g_testImage.copy()
        elif cameraReader is not None:
            # Get a frame from the async camera reader
            raw = cameraReader.Read()

        if raw is not None and firstFrameSkipped:

            ### This is the primary frame processing block
            fpsCounter.tick()
            gameTarget.evaluateCandidatePair(findTargetPair(raw, params))
            if gameTarget.confirmed:
                horizontalOffset = gameTarget.centerX - (g_cameraFrameWidth / 2.0)
                if gameTarget.confirmedType == gameTarget.LIFT_TYPE:
                    distance = liftDistance.CalculateDistance(gameTarget.patchA.height)*100
                else:
                    distance = boilerDistance.CalculateDistance(gameTarget.patchA.width)*100
                payload = {
                    'horizontalOffset': horizontalOffset,
                    'targetDistance': round(distance),
                    'hasTarget': True,
                    'targetAge': gameTarget.confirmedAge,
                    'fps': round(fpsCounter.getFramerate())}
            else:
                payload = {
                    'hasTarget': False,
                    'fps': round(fpsCounter.getFramerate())}

            if g_debugMode:
                if gameTarget.confirmed:
                    targetDistance = (abs(gameTarget.patchA.centerX - gameTarget.patchB.centerX))
                    cv2.putText(raw, gameTarget.confirmedType + "Distance:" + str(round(5.179*targetDistance - 465.135)) + "Area:" + str(round((gameTarget.patchA.area / 10))),
                                (g_cameraFrameWidth - 600, 13 + 6),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 1)
                if fpsDisplay:
                    cv2.putText(raw, "{:.0f} fps".format(fpsCounter.getFramerate()),
                                (g_cameraFrameWidth - 100, 13 + 6),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 1)
                cv2.imshow("raw", raw)

            # pass telemetry to robot
            #printif(json.dumps(payload))
            client.publish(MQTT_TOPIC_TARGETING, json.dumps(payload))

        if raw is not None:
            firstFrameSkipped = True
        if fpsDisplay and fpsInterval.hasElapsed():
            print "{0:.1f} fps (processing)".format(fpsCounter.getFramerate())
            if cameraReader is not None:
                print "{0:.1f} fps (camera)".format(cameraReader.fps.getFramerate())


        # Monitor for control keystrokes in debug mode
        if g_debugMode:
            keyPress = cv2.waitKey(1)
            if keyPress != -1:
                keyPress = keyPress & 0xFF
            if keyPress == ord("q"):
                break
    # Clean up
    printif("Cleaning up")
    if cameraReader is not None:
        cameraReader.Stop()

    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()

    printif("End of main function")

parser = argparse.ArgumentParser(description="OpenCV-based target telemetry, FRC 5582, 2017")
parser.add_argument("--release", dest="releaseMode", action="store_const", const=True, default=not g_debugMode,
                    help="hides all debug windows (default: False)")
args = parser.parse_args()
g_debugMode = not args.releaseMode

main()
time.sleep(2)
if not g_debugMode:
    os.system('shutdown now -h')
exit()