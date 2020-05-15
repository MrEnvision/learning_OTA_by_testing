import math
import random
from tester import testLTWs, testDTWs
from system import systemOutput
from timedWord import TimedWord, ResetTimedWord


# membership query
def TQs(LTWs, targetSys, mqNum):
    mqNum += 1
    LRTWs, value = testLTWs(LTWs, targetSys)
    return LRTWs, value, mqNum


# equivalence query - ctx is DRTWs
def EQs(hypothesis, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum):
    flag = True  # True -> equivalence，False -> not equivalence
    ctx = []
    testSum = (math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon
    i = 1
    toSinkCount = 0
    while i <= testSum:
        sample = sampleGeneration(hypothesis.inputs, upperGuard, stateNum, targetSys)  # sample is DTWs
        DRTWs, value = getHpyDTWsValue(sample, hypothesis)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        i += 1
        testNum += 1
        # compare result
        if realValue == -1:
            toSinkCount += 1
            if realValue == -1 and value == 1:
                flag = False
                ctx = realDRTWs
                break
            else:
                i -= 1
                continue
        elif (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            flag = False
            ctx = realDRTWs
            break
        # if realValue == -1:
        #     continue
        # elif (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
        #     flag = False
        #     ctx = realDRTWs
        #     break
    print('# test to sink State: ', toSinkCount, ' testNum of current EQ: ', i)
    return flag, ctx, testNum


# 根据设定的分布随机采样 - PAC采样
def sampleGeneration(inputs, upperGuard, stateNum, targetSys):
    sample = []
    # length = random.randint(1, stateNum * 2)
    length = random.randint(1, math.ceil(stateNum * 1.2))
    dic = targetSys.getInputsDic()

    curState = targetSys.initState
    nowTime = 0

    for i in range(length):
        curInputs = dic[curState]
        input = curInputs[random.randint(0, len(curInputs) - 1)]
        time = random.randint(0, upperGuard * 2 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.1
        temp = TimedWord(input, time)
        sample.append(temp)

        curState, value, resetFlag = systemOutput(temp, nowTime, curState, targetSys)
        if resetFlag:
            nowTime = 0
        else:
            nowTime = nowTime + time
        if value == -1:
            break
    return sample


def sampleGeneration_old_3(inputs, upperGuard, stateNum, targetSys):
    sample = []
    length = random.randint(1, stateNum * 2)
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 2 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.1
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


def sampleGeneration_old_1(inputs, upperGuard, stateNum, targetSys):
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


# --------------------------------- 辅助函数 ---------------------------------

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
