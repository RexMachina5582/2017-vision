import numpy as np
import cv2
import argparse

from GameTarget import GameTarget
from RealtimeInterval import RealtimeInterval
from CVParameterGroup import CVParameterGroup
import TriangleSimilarityDistanceCalculator as distanceCalc
import CameraReaderAsync
from WeightedFramerateCounter import WeightedFramerateCounter

''' hunt.py
	Computer vision main module for Rex Machina 2017 competition
'''

# Tunable parameters
SAMPLE_PARAMETER = 1

g_debugMode = True
g_cameraFrameWidth = None
g_cameraFrameHeight = None
g_testImage = None

def printif(message):
    if g_debugMode:
        print message

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


def main():
    params = CVParameterGroup("Sliders", g_debugMode)
    setCVParameters(params)

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

    # Loop on acquisition
    while (True):

        if g_testImage is not None:
            # Use a file image if provided, for testing
            raw = g_testImage.copy()
        elif cameraReader is not None:
            # Get a frame from the async camera reader
            raw = cameraReader.Read()

        if raw is not None and firstFrameSkipped:

            ### This is the primary frame processing block
            if g_debugMode:
                if fpsDisplay:
                    cv2.putText(raw, "{:.0f} fps".format(fpsCounter.getFramerate()),
                                (g_cameraFrameWidth - 100, 13 + 6),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 1)
                cv2.imshow("raw", raw)

            fpsCounter.tick()

            # acquire a target pair
            # Use the findTarget function modified to return 2 largest contours, not the 1 largest.
            # We'll put these 2 countours into a list. Maybe make
            # the list be gameTarget.candidateCountourPair

            # classify the target pair, if there is one; otherwise the confirmed attribute is false and age is 0.
            # Use a new function that compares X and Y of the target pair and determines if they are within
            # a range of pixel tolerance that means they are aligned.
            # Set a target type string of either "peg" or "boiler" or "none". Increment the target age counter.
            # gameTarget.confirmed = True
            # gameTarget.confirmedType = "xxx"
            # gameTarget.confirmedAge = <int>

            # Now we need a bounding box. Use getTargetBoxTight from vision.py. It returns a list of tuples,
            # an array of arrays. Put it in gameTarget.boundingBox

            # determine target skew/off-axis; note that Team 5495 does not seem to use this in robot code,
            # maybe it is used in their dashboard.

            # determine target horizontal offset (lateral)

            # determine target range

            # determine age of target

            # pass telemetry to robot

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
exit()
