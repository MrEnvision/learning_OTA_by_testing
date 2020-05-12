from teacher import sampleGeneration, getHpyDTWsValue
from tester import testDTWs_2


def getPassingRate(learnedSys, targetSys, upperGuard, stateNum, testNum):
    failNum = 0
    passNum = 0
    for i in range(testNum):
        sample = sampleGeneration(learnedSys.inputs, upperGuard, stateNum)  # sample is DTWs
        LRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realLRTWs, realValue = testDTWs_2(sample, targetSys)
        if LRTWs == realLRTWs:
            if value != realValue:
                failNum += 1
            else:
                passNum += 1
        else:
            failNum += 1
    return passNum / testNum
