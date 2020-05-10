from teacher import sampleGeneration, getHpyDTWsValue, testDTWs


def getError(learnedSys, targetSys, upperGuard, stateNum):
    testNum = 20000
    failNum = 0
    passNum = 0
    for i in range(testNum):
        sample = sampleGeneration(learnedSys.inputs, upperGuard, stateNum)  # sample is DTWs
        LRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realLRTWs, realValue = testDTWs(sample, targetSys)
        if LRTWs == realLRTWs:
            if value != realValue:
                failNum += 1
            else:
                passNum += 1
        else:
            failNum += 1
    # print('failNum', failNum, ' passNum', passNum)
    return passNum / testNum
