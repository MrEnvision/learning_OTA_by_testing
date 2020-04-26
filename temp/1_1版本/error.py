from comparator import buildMergeOTA, buildComplementOTA
import numpy as np
import scipy.stats as st


def computeError(hypothesis, targetSys, upperGuard):
    error = 0
    mergeOTA = buildMergeOTA(hypothesis, targetSys)
    complementOTA = buildComplementOTA(mergeOTA)
    if complementOTA.errorState == 'Null':
        return 0
    length = len(complementOTA.states)
    array = np.ones((length, length)) * 0
    tempArray = np.ones((length, length)) * 0
    for n in range(length):
        tempArray[n][n] = 1
    stateName_dict = {}
    for i in range(len(complementOTA.states)):
        stateName_dict[complementOTA.states[i].stateName] = i
    for i in complementOTA.trans:
        source = stateName_dict[i.source]
        target = stateName_dict[i.target]
        volume = computeVolume(i.guards, upperGuard)
        array[source][target] += volume
    errorIndex = stateName_dict[complementOTA.errorState]
    array[errorIndex][errorIndex] += (len(hypothesis.inputs) * upperGuard)
    initIndex = stateName_dict[complementOTA.initState]
    stateNum = len(targetSys.states)
    for m in range(1, 2 * stateNum):
        pl = 2 * (st.norm.cdf(m, loc=0, scale=stateNum + 1) - st.norm.cdf(m - 1, loc=0, scale=stateNum + 1))
        tempArray = np.dot(tempArray, array)
        vi = tempArray[initIndex, errorIndex]
        error += (pl * vi / ((len(targetSys.inputs) * upperGuard) ** m))
    return error


def computeVolume(guards, upperGuard):
    volume = 0
    for guard in guards:
        minType, maxType = guard.guard.split(',')
        minNum = float(minType[1:])
        if maxType[:-1] == '+':
            maxNum = upperGuard
        else:
            maxNum = float(maxType[:-1])
        volume += (maxNum - minNum)
    return volume
