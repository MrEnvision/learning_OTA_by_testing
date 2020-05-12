from system import systemOutput, systemTest
from timedWord import TimedWord, ResetTimedWord, DRTW_to_LRTW


# logical-timed test，无效或sink即终止，并补全
def testLTWs(LTWs, targetSys):
    if not LTWs:
        if targetSys.initState in targetSys.acceptStates:
            value = 1
        else:
            value = 0
        return [], value
    else:
        LRTWs = []
        value = None
        nowTime = 0
        curState = targetSys.initState
        for ltw in LTWs:
            if ltw.time < nowTime:
                value = -1
                LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
                break
            else:
                DTW = TimedWord(ltw.input, ltw.time - nowTime)
                curState, value, resetFlag = systemTest(DTW, nowTime, curState, targetSys)
                if resetFlag:
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
                    nowTime = 0
                else:
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, False))
                    nowTime = ltw.time
                if value == -1:
                    break
        # 补全
        lenDiff = len(LTWs) - len(LRTWs)
        if lenDiff != 0:
            temp = LTWs[len(LRTWs):]
            for i in temp:
                LRTWs.append(ResetTimedWord(i.input, i.time, True))
        return LRTWs, value


# delay-timed test
def testDTWs(DTWs, targetSys):
    DRTWs, value = systemOutput(DTWs, targetSys)
    LRTWs = DRTW_to_LRTW(DRTWs)
    return LRTWs, value


# delay-timed test - 输入DTWs，返回DRTWs
def testDTWs_2(DTWs, targetSys):
    DRTWs, value = systemOutput(DTWs, targetSys)
    return DRTWs, value
