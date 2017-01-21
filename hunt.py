import numpy as np
import cv2

import GameTarget
import RealtimeInterval
import CVParameterGroup
import TriangleSimilarityDistanceCalculator as distanceCalc

''' hunt.py
	Computer vision main module for Rex Machina 2017 competition
'''

# Tunable parameters
SAMPLE_PARAMETER = 1

def createCamera():
	# return a camera object with exposure and contrast set 
    global cameraFrameWidth
    global cameraFrameHeight
    
    camera = cv2.VideoCapture(0)
    #No camera's exposure goes this low, but this will set it as low as possible
    #camera.set(cv2.cv.CV_CAP_PROP_EXPOSURE,-100)    
    #camera.set(cv2.cv.CV_CAP_PROP_FPS, 15)
    #camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    #camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
    cameraFrameWidth = int(camera.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    cameraFrameHeight = int(camera.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    return camera

	 
def main():
	
	# Start the camera
	
	target = GameTarget

	# Loop on acquisition

		# acquire a target pair

		# classify the target pair

		# determine target offset (lateral)
		
		# determine target range

		# determine age of target
		
		# pass telemetry to robot


main()
