import math
import random
from timedWord import TimedWord, ResetTimedWord, LRTW_to_DRTW
from tester import testLTWs, testDTWs, testDTWs_2


# 成员查询
def TQs(LTWs, targetSys, mqNum):
    flag, LRTWs, value = targetSys.isLTWsTested(LTWs)
    if flag:
        return LRTWs, value, mqNum
    else:
        mqNum += 1
        LRTWs, value = testLTWs(LTWs, targetSys)
        targetSys.addTestResult(LRTWs, value)
        return LRTWs, value, mqNum


# 等价查询 - ctx为DRTWs
def EQs(hypothesis, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum):
    flag = True  # 等价True，不等价False
    ctx = []
    testSum = (math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon  # 人为定义最大测试次数
    i = 1
    while i <= testSum:
        sample = sampleGeneration(hypothesis.inputs, upperGuard, stateNum)  # sample is DTWs
        # 猜测结果 - 全
        DRTWs, value = getHpyDTWsValue(sample, hypothesis)
        # 目标结果 - 全
        realDRTWs, realValue = testDTWs_2(sample, targetSys)
        testNum += 1
        # 结果比较
        # if realValue != value:
        if (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            flag = False
            ctx = realDRTWs
            break
        i += 1
    return flag, ctx, testNum


# 根据设定的分布随机采样 - PAC采样
def sampleGeneration(inputs, upperGuard, stateNum):
    sample = []
    length = math.ceil(random.gauss(stateNum, stateNum / 2))
    while length < 0:
        length = math.ceil(random.gauss(stateNum, stateNum / 2))
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 3) / 2
        if time > upperGuard:
            time = upperGuard
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


# 假设下输入DTWs，获得DRTWs+value
def getHpyDTWsValue(sample, hypothesis):
    DRTWs = []
    nowTime = 0
    curState = hypothesis.initState
    for dtw in sample:
        if curState == hypothesis.sinkState:
            DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
        else:
            time = dtw.time + nowTime
            newLTW = TimedWord(dtw.input, time)
            for tran in hypothesis.trans:
                if tran.source == curState and tran.isPass(newLTW):
                    curState = tran.target
                    if tran.isReset:
                        nowTime = 0
                        isReset = True
                    else:
                        nowTime = time
                        isReset = False
                    DRTWs.append(ResetTimedWord(dtw.input, dtw.time, isReset))
                    break
    if curState in hypothesis.acceptStates:
        value = 1
    elif curState == hypothesis.sinkState:
        value = -1
    else:
        value = 0
    return DRTWs, value
