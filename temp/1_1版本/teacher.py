import math
import random
from timedWord import TimedWord, ResetTimedWord, LRTW_to_DRTW
from tester import testLTWs


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
    testSum = (math.log(1 / epsilon) + math.log(2) * (eqNum + 1)) / delta  # 人为定义最大测试次数
    print("testSum", testSum)
    i = 1
    while i <= testSum:
        sample = sampleGeneration(hypothesis.inputs, upperGuard, stateNum)  # sample is LTWs
        # 猜测结果 - 全
        LRTWs, value = getHpyLTWsValue(sample, hypothesis)
        # 目标结果 - 全
        realLRTWs, realValue, testNum = TQs(sample, targetSys, testNum)
        # 结果比较
        if LRTWs == realLRTWs:
            if value != realValue:
                print('condition1')
                print('sample', [i.show() for i in sample])
                print('1—', value, ' 2-', realValue)
                flag = False
                ctx = realLRTWs
                break
        else:
            print('condition2')
            print('sample', [i.show() for i in sample])
            print('1—', [i.show() for i in LRTWs])
            print('2-', [i.show() for i in realLRTWs])
            flag = False
            minLRTWs = []
            for i in range(len(realLRTWs)):
                minLRTWs.append(realLRTWs[i])
                if realLRTWs[i] != LRTWs[i]:
                    break
            ctx = minLRTWs
            break
        i += 1
    return flag, ctx, testNum


# 根据设定的分布随机采样 - PAC采样
def sampleGeneration(inputs, upperGuard, stateNum):
    sample = []
    length = math.ceil(abs(random.normalvariate(0, stateNum + 1)))
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 2) / 2
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


def getHpyLTWsValue(LTWs, hypothesis):
    LRTWs = []
    nowTime = 0
    curState = hypothesis.initState
    for ltw in LTWs:
        if ltw.time < nowTime:
            curState = hypothesis.sinkState
            LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
            break
        else:
            for tran in hypothesis.trans:
                if tran.source == curState and tran.isPass(ltw):
                    curState = tran.target
                    if tran.isReset:
                        nowTime = 0
                        isReset = True
                    else:
                        nowTime = ltw.time
                        isReset = False
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, isReset))
                    break
    # 补全
    lenDiff = len(LTWs) - len(LRTWs)
    if lenDiff != 0:
        temp = LTWs[len(LRTWs):]
        for i in temp:
            LRTWs.append(ResetTimedWord(i.input, i.time, True))
    if curState in hypothesis.acceptStates:
        value = 1
    elif curState == hypothesis.sinkState:
        value = -1
    else:
        value = 0
    return LRTWs, value
