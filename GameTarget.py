import numpy as np
import cv2


class Patch:
    def __init__(self, countour):
        M = cv2.moments(countour)
        self.centerX = int(M["m10"] / M["m00"])
        self.centerY = int(M["m01"] / M["m00"])
        self.area = int(M["m00"])
        self.width = int(M["m10"])
        self.height = int(M["m01"])


class GameTarget:

    LIFT_TYPE = "lift"
    BOILER_TYPE = "boiler"
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
        self.centerY = (self.patchA.centerY + self.patchB.centerY) / 2
        self.centerX = (self.patchA.centerX + self.patchB.centerX) / 2


        # Patch A is the larger countour. Calculate its ratio, B as a % of A
        patchRatio = self.patchA.area/self.patchB.area

        if (abs(self.patchA.centerY - self.patchB.centerY) < GameTarget.Y_CONGRUENCE_THRESHOLD
            and (abs(GameTarget.PEG_LEFT_TO_RIGHT_RATIO-patchRatio) < GameTarget.TARGET_RATIO_VARIANCE)):
            self.__confirmTarget(self.LIFT_TYPE)
            return True
        elif (abs(self.patchA.centerX - self.patchB.centerX) < GameTarget.X_CONGRUENCE_THRESHOLD
            and (abs(GameTarget.BOILER_BOTTOM_TO_TOP_RATIO-patchRatio) < GameTarget.TARGET_RATIO_VARIANCE)):
            self.__confirmTarget(self.BOILER_TYPE)
            return True

        self.__reset()
        return False
