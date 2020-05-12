import os
from equiv import equivalence
from equiv import ota as old_ota
from equiv import interval as old_interval
from hypothesis import OTA, OTATran
from system import buildSystem
from comparator import buildCanonicalOTA
from system import systemOutput
from timedWord import TimedWord, ResetTimedWord


def transform_system(system, name, flag):
    """Transform system in learning_OTA_by_testing to system in equiv.
    
    """
    locations = []
    for loc in system.states:
        is_init = (loc == system.initState)
        is_accept = (loc in system.acceptStates)
        is_sink = (loc == system.sinkState)
        locations.append(old_ota.Location(loc, is_init, is_accept, flag, is_sink))

    trans = []
    for tran in system.trans:
        constraints = []
        for guard in tran.guards:
            constraints.append(old_interval.Constraint(guard.guard))
        trans.append(old_ota.OTATran(tran.tranId, tran.source, tran.input, constraints,
                                     tran.isReset, tran.target, flag))

    ota = old_ota.OTA(name, system.inputs, locations, trans, system.initState, system.acceptStates)
    return ota


def hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, targetFullSys, mqNum, metric):
    """
    stableHpy: old candidate automata
    hypothesisOTA: new candidate automata
    upperGuard: maximum time value
    targetSys: teacher automata
    targetFullSys: complete teacher automata
    mqNum: number of membership queries
    metric: distance between hypothesisOTA and targetSys

    """
    # 第一次不进行比较
    if stableHpy is None:
        return True, [], mqNum, metric

    sys = transform_system(stableHpy, "A", "s")
    sys2 = transform_system(hypothesisOTA, "B", "q")

    res, w_pos = equivalence.ota_inclusion(upperGuard+1, sys, sys2)
    # dtw_pos is accepted by sys2 but not sys.
    if not res:
        dtw_pos = equivalence.findDelayTimedwords(w_pos, 's', sys2.sigma)
        print(dtw_pos)

    res2, w_neg = equivalence.ota_inclusion(upperGuard+1, sys2, sys)
    # dtw_neg is accepted by sys but not sys2.
    if not res2:
        dtw_neg = equivalence.findDelayTimedwords(w_neg, 's', sys.sigma)
        print(dtw_neg)

    if res and res2:
        print('_____________________________')
        stableHpy.showOTA()
        print('_____________________________')
        hypothesisOTA.showOTA()
        raise NotImplementedError('hpyCompare should always find a difference')
    print(type(w_pos))
    print(type(w_neg))
    if res and not res2:
        hpy_flag, ctx = 0, dtw_neg
    elif res2 and not res:
        hpy_flag, ctx = 1, dtw_pos
    elif len(w_pos.lw) <= len(w_neg.lw):
        hpy_flag, ctx = 1, dtw_pos
    else:
        hpy_flag, ctx = 0, dtw_neg

    flag = True
    newCtx = []
    tempCtx = []
    for i in ctx:
        tempCtx.append(TimedWord(i.action, i.time))
    realDRTWs, realValue = testDTWs_2(tempCtx, targetSys)
    if (realValue == 1 and hpy_flag != 1) or (realValue != 1 and hpy_flag == 1):
        flag = False
        newCtx = realDRTWs

    return flag, newCtx, mqNum + 1, ''


# delay-timed test - 输入DTWs，返回DRTWs
def testDTWs_2(DTWs, targetSys):
    DRTWs, value = systemOutput(DTWs, targetSys)
    return DRTWs, value


# 假设下输入DTWs，获得DRTWs+value
def getHpyDTWsValue_2(sample, teacher):
    DRTWs = []
    nowTime = 0
    curState = teacher.initState
    for dtw in sample:
        if curState == teacher.sinkState:
            DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
        else:
            time = dtw.time + nowTime
            newLTW = TimedWord(dtw.input, time)
            for tran in teacher.trans:
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
    if curState in teacher.acceptStates:
        value = 1
    elif curState == teacher.sinkState:
        value = -1
    else:
        value = 0
    return DRTWs, value


if __name__ == "__main__":
    experiments_path = os.getcwd() + '/Automata/'
    A = buildSystem(experiments_path + 'example3.json')
    AA = buildCanonicalOTA(A)

    sys = transform_system(AA, "A", "s")
    sys.show()

    H = buildSystem(experiments_path + 'example3_1.json')
    HH = buildCanonicalOTA(H)

    sys2 = transform_system(HH, "B", "q")
    sys2.show()

    max_time_value = 10

    # hpyCompare(AA, HH, max_time_value, None, None, 0, 0.0)

    res, w_pos = equivalence.ota_inclusion(max_time_value, sys, sys2)
    # drtw_pos is accepted by sys2 but not sys.
    # drtw_pos = equivalence.dTWs_to_dRTWs(w_pos, 's', sys2)

    res2, w_pos2 = equivalence.ota_inclusion(max_time_value, sys2, sys)
    # drtw_pos2 is accepted by sys but not sys2.
    # drtw_pos2 = equivalence.dTWs_to_dRTWs(w_pos2, 's', sys)

    print(res)
    # print(drtw_pos)
    print(res2)
    # print(drtw_pos2)

    print('_____________________________')
    dtws = [TimedWord('a', 6), TimedWord('b', 6)]
    realDRTWs1, realValue1 = getHpyDTWsValue_2(dtws, AA)
    realDRTWs2, realValue2 = getHpyDTWsValue_2(dtws, HH)
    print([i.show() for i in dtws])
    print(realValue1)
    print(realValue2)
