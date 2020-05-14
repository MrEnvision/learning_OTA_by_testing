from teacher import sampleGeneration, getHpyDTWsValue
from tester import testDTWs


def validate(learnedSys, targetSys, upperGuard, stateNum, testNum):
    failNum = 0
    for i in range(testNum):
        sample = sampleGeneration(learnedSys.inputs, upperGuard, stateNum, targetSys)
        DRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        if (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            failNum += 1
        # if realValue != value:
        #     failNum += 1
        # else:
        #     passNum += 1
    return (testNum - failNum) / testNum
