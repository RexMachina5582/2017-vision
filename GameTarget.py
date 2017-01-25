import numpy as np
import cv2


class Patch:
    def __init__(self, countour):
        # Reference our workshop code to find out how to use cv2.moments to calculate x, y, and area.
        # Our trackTarget.py module is now in this project directory for easy reference.
        self.centerX = 0
        self.centerY = 0
        self.area = 0

class GameTarget:

    # Boiler target patches have congruent X for center points within this many pixels
    X_CONGRUENCE_THRESHOLD = 10
    # The larger boiler target patch is about double the area of the smaller
    BOILER_BOTTOM_TO_TOP_RATIO = 0.5

    # Peg target patches have congruent Y for center points within this many pixels
    Y_CONGRUENCE_THRESHOLD = 15
    # Peg target patches are about equal in area
    PEG_LEFT_TO_RIGHT_RATIO = 1.0

    # We accept this variance from the theoretical when comparing the patch areas as a ratio
    TARGET_RATIO_VARIANCE = 0.15


    def __init__(self, debug=False):
        self.debugFlag = debug
        self.__reset()

    def __reset(self):
        self.countourPair = []
        self.confirmed = False
        self.confirmedAge = 0
        self.confirmedType = None
        self.boundingBox = { }

    def __confirmTarget(self, type):
        if self.confirmed is True:
            self.confirmedAge += 1
            return
        self.confirmed = True
        self.confirmedType = type
        self.confirmedAge = 1

    def evaluateCandidatePair(self, countourPair):
        if countourPair is None:
            self.__reset()
            return False

        self.countourPair = countourPair
        self.patchA = Patch(countourPair[0])
        self.patchB = Patch(countourPair[1])

        # Patch A is the larger countour. Calculate its ratio, B as a % of A
        patchRatio = 0.9

        # if / elif statements. Does the absolute difference of patch X values fit within the X threshold?
        # And does the absolute difference of theoretical and actual patch ratios fit within variance?
        # If so, you've found the boiler target. You should confirm it. Then, "elif", do something very similar
        # for the patch Y values and target ratio that would qualify a peg target. If you do confirm a target,
        # make sure to return true before hitting the reset further down.

        self.__reset()
        return False
