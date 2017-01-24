import numpy as np
import cv2


class GameTarget:
    def __init__(self, debug=False):
        self.debugFlag = debug
        self.candidateCountourPair = { }
        self.confirmed = False
        self.confirmedAge = 0
        self.confirmedType = None
        self.boundingBox = { }

    def targetOffset(self):
        # Take target pair and type, calculate center, and compare with
        # desired location of target center for this target type.
        # Return offset as positive or negative pixel count.
        pass

    def targetType(self):
        # Take a pair of target contours and determine if they are
        # likely to be the boiler, the peg, or noise.
        pass

    def targetPair(self):
        # Define a mask and apply it to the current frame.
        # Return the 2 largest countours matching the mask.
        pass
