import os
from equiv import equivalence
from equiv import ota as old_ota
from equiv import interval as old_interval
from hypothesis import OTA, OTATran
from system import buildSystem
from comparator import buildCanonicalOTA


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
    sys = transform_system(stableHpy, "A", "s")
    sys2 = transform_system(hypothesisOTA, "B", "q")

    res, w_pos = equivalence.ota_inclusion(upperGuard, sys, sys2)
    # dtw_pos is accepted by sys2 but not sys.
    if not res:
        dtw_pos = equivalence.findDelayTimedwords(w_pos, 's', sys2.sigma)
        print(dtw_pos)

    res2, w_neg = equivalence.ota_inclusion(upperGuard, sys2, sys)
    # dtw_neg is accepted by sys but not sys2.
    if not res2:
        dtw_neg = equivalence.findDelayTimedwords(w_neg, 's', sys.sigma)
        print(dtw_neg)

    if res and res2:
        raise NotImplementedError('hpyCompare should always find a difference')

    if res and not res2:
        hpy_flag, ctx = 0, dtw_neg
    elif res2 and not res:
        hpy_flag, ctx = 1, dtw_pos
    elif len(w_pos) <= len(w_neg):
        hpy_flag, ctx = 1, dtw_pos
    else:
        hpy_flag, ctx = 0, dtw_neg

    return hpy_flag, ctx, mqNum + 1, ''


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
    experiments_path = os.getcwd()+"\\Automata\\"
    A = buildSystem(experiments_path+'example3.json')
    AA = buildCanonicalOTA(A)

    sys = transform_system(AA, "A", "s")
    sys.show()

    H = buildSystem(experiments_path+'example3_1.json')
    HH = buildCanonicalOTA(H)

    sys2 = transform_system(HH, "B", "q")
    sys2.show()

    max_time_value = 7

    hpyCompare(AA, HH, max_time_value, None, None, 0, 0.0)

    # res, w_pos = equivalence.ota_inclusion(max_time_value, sys, sys2)
    # # drtw_pos is accepted by sys2 but not sys.
    # drtw_pos = equivalence.dTWs_to_dRTWs(w_pos, 's', sys2)

    # res2, w_pos2 = equivalence.ota_inclusion(max_time_value, sys2, sys)
    # # drtw_pos2 is accepted by sys but not sys2.
    # drtw_pos2 = equivalence.dTWs_to_dRTWs(w_pos2, 's', sys)

    # print(res)
    # print(drtw_pos)
    # print(res2)
    # print(drtw_pos2)
