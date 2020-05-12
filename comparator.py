import copy
import math
import timeInterval as timeInterval
from hypothesis import OTA, OTATran
from teacher import TQs
from timedWord import LRTW_to_DRTW, ResetTimedWord


class ConnectOTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState


class ComplementOTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState, errorState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState
        self.errorState = errorState


class State(object):
    def __init__(self, stateName, firstId, secondId):
        self.stateName = stateName
        self.firstId = firstId
        self.secondId = secondId


def hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, targetFullSys, mqNum, metric):
    # 第一次不进行比较
    if stableHpy is None:
        return True, [], mqNum, metric

    # 计算两个假设的最小区分序列
    mergeOTA = buildMergeOTA(stableHpy, hypothesisOTA)
    complementOTA = buildComplementOTA(mergeOTA)
    compareTrace = getMinCtxList(complementOTA)  # 返回LTWs

    flag = True
    ctx = []
    for trace in compareTrace:
        # 假设结果
        LRTWs, value = getHpyLTWsValue(trace, hypothesisOTA)
        # 目标结果
        realLRTWs, realValue, mqNum = TQs(trace, targetSys, mqNum)
        # 结果比较
        if LRTWs == realLRTWs:
            if value != realValue:
                flag = False
                ctx = realLRTWs
                break
        else:
            flag = False
            minLRTWs = []
            for i in range(len(realLRTWs)):
                minLRTWs.append(realLRTWs[i])
                if realLRTWs[i] != LRTWs[i]:
                    break
            ctx = minLRTWs
            break
    ctx = LRTW_to_DRTW(ctx)
    # 计算当前假设的距离
    mergeSys = buildMergeOTA(targetFullSys, hypothesisOTA)
    complementSys = buildComplementOTA(mergeSys)
    newMetric = distanceMetric(complementSys)
    print("Current hypothesis metric: ", newMetric)
    if flag and newMetric > metric:
        return "Metric Error"
    return flag, ctx, mqNum, newMetric


# Step1 补全targetSys
def buildCanonicalOTA(targetSys):
    inputs = targetSys.inputs
    states = targetSys.states
    trans = targetSys.trans
    initState = targetSys.initState
    acceptStates = targetSys.acceptStates

    sinkFlag = False
    newTrans = []
    sinkState = None
    tranNumber = len(targetSys.trans)

    for state in targetSys.states:
        guardDict = {}
        for input in inputs:
            guardDict[input] = []
        for tran in trans:
            if tran.source == state:
                for input in inputs:
                    if tran.input == input:
                        for guard in tran.guards:
                            guardDict[input].append(guard)
        for key, value in guardDict.items():
            if len(value) > 0:
                addGuards = complementIntervals(value)
            else:
                addGuards = [timeInterval.Guard('[0,+)')]
            if len(addGuards) > 0:
                sinkState = 'sink'
                sinkFlag = True
                for guard in addGuards:
                    tempTran = OTATran(tranNumber, state, key, [guard], True, sinkState)
                    tranNumber = tranNumber + 1
                    newTrans.append(tempTran)
    if sinkFlag:
        states.append(sinkState)
        for tran in newTrans:
            trans.append(tran)
        for input in inputs:
            guards = [timeInterval.Guard('[0,+)')]
            tempTran = OTATran(tranNumber, sinkState, input, guards, True, sinkState)
            tranNumber = tranNumber + 1
            trans.append(tempTran)
    newOTA = OTA(inputs, states, trans, initState, acceptStates, sinkState)
    return newOTA


# Step2 计算合并自动机
def buildMergeOTA(hypOTA, targetOTA):
    inputs = hypOTA.inputs
    states = []
    trans = []
    initStateName = str(hypOTA.initState) + '_' + str(targetOTA.initState)
    acceptStates = []
    transNum = 0
    sinkState = None
    tempStates = []
    finalStates = []
    initState = State(initStateName, hypOTA.initState, targetOTA.initState)
    if hypOTA.initState in hypOTA.acceptStates and targetOTA.initState in targetOTA.acceptStates:
        acceptStates.append(initStateName)
    states.append(initState)
    tempStates.append(initState)
    while len(tempStates) != 0:
        state1 = tempStates[0].firstId
        state2 = tempStates[0].secondId
        temp1 = []  # [input,guard,target,output,isReset]
        temp2 = []
        for tran in hypOTA.trans:
            if tran.source == state1:
                if tran.target == hypOTA.sinkState:
                    output = -1
                elif tran.target in hypOTA.acceptStates:
                    output = 1
                else:
                    output = 0
                temp1.append([tran.input, tran.guards, tran.target, output, tran.isReset])
        for tran in targetOTA.trans:
            if tran.source == state2:
                if tran.target == targetOTA.sinkState:
                    output = -1
                elif tran.target in targetOTA.acceptStates:
                    output = 1
                else:
                    output = 0
                temp2.append([tran.input, tran.guards, tran.target, output, tran.isReset])
        for i in range(len(temp1)):
            for j in range(len(temp2)):
                if temp1[i][0] == temp2[j][0] and temp1[i][3] == temp2[j][3] and temp1[i][4] == temp2[j][4]:
                    guards1 = temp1[i][1]
                    guards2 = temp2[j][1]
                    guards, flag = intersectionGuard(guards1, guards2)
                    if flag:
                        source = tempStates[0].stateName
                        target = str(temp1[i][2]) + '_' + str(temp2[j][2])
                        tempTran = OTATran(transNum, source, temp1[i][0], guards, temp1[i][4], target)
                        trans.append(tempTran)
                        transNum += 1
                        if not alreadyHas(target, tempStates, finalStates):
                            newState = State(target, temp1[i][2], temp2[j][2])
                            if temp1[i][3] == 1:
                                acceptStates.append(newState.stateName)
                            elif temp1[i][3] == -1:
                                sinkState = newState.stateName
                            states.append(newState)
                            tempStates.append(newState)
        finalStates.append(tempStates[0])
        tempStates.remove(tempStates[0])
    mergeOTA = ConnectOTA(inputs, states, trans, initStateName, acceptStates, sinkState)
    return mergeOTA


# Step3 计算OTA的补
def buildComplementOTA(mergeOTA):
    tempOTA = copy.deepcopy(mergeOTA)
    inputs = tempOTA.inputs
    states = tempOTA.states
    trans = tempOTA.trans
    initState = tempOTA.initState
    acceptStates = tempOTA.acceptStates
    sinkState = tempOTA.sinkState
    tranId = len(trans)
    stateId = len(states)
    flag = False
    errorState = State(stateId, 'Null', "Null")
    for state in states:
        need = {}
        exist = {}
        for input in inputs:
            need[input] = []
            exist[input] = []
        for tran in trans:
            if tran.source == state.stateName:
                exist[tran.input] += tran.guards
        for key, i in exist.items():
            guards = complementIntervals(i)
            if len(guards) > 0:
                flag = True
                for j in range(len(guards)):
                    if guards[j] not in i:
                        need[key].append(guards[j])
        for key, value in need.items():
            if len(value) > 0:
                newTran = OTATran(tranId, state.stateName, key, value, True, errorState.stateName)
                trans.append(newTran)
    if flag:
        states.append(errorState)
    else:
        errorState = State('Null', 'Null', 'Null')
    complementOTA = ComplementOTA(inputs, states, trans, initState, acceptStates, sinkState, errorState.stateName)
    return complementOTA


# Step4 计算最短反例
def getMinCtxList(complementOTA):
    # 获得每个状态对应的连接状态 {"0":["0","1","2"]}
    stateDict = {}
    for s in complementOTA.states:
        stateDict[s.stateName] = []
        for t in complementOTA.trans:
            if t.source == s.stateName:
                if t.target not in stateDict[s.stateName]:
                    stateDict[s.stateName].append(t.target)
    # 获得最短反例路径
    ctxList = []
    allPath = findAllPath(stateDict, complementOTA.initState, complementOTA.errorState)
    allPath.sort(key=getLength)
    if len(allPath) == 0:
        return ctxList
    else:
        for i in range(len(allPath)):
            flag = False
            # 计算最短反例
            compareTrace = []
            trace, nowTime = getStateTrace(complementOTA, allPath[i])
            compareTrace += trace
            firstState = allPath[i][-1]
            secondState = allPath[i][-2]
            for tran in complementOTA.trans:
                if tran.source == secondState and tran.target == firstState:
                    timeList = getTimeList(tran.guards, nowTime)  # 目前设置仅取一个值
                    if not timeList:
                        continue
                    for time in timeList:
                        flag = True
                        lrtw = ResetTimedWord(tran.input, time, True)
                        tempTrace = compareTrace + [lrtw]
                        ctxList.append(tempTrace)
                    break
            if flag:
                tempCtxList = []
                for ctx in ctxList:
                    if ctx not in tempCtxList:
                        tempCtxList.append(ctx)
                return tempCtxList
        return ctxList


# Step5 计算距离度量
def distanceMetric(complementOTA):
    # 获得每个状态对应的连接状态 {"0":["0","1","2"]}
    stateDict = {}
    for s in complementOTA.states:
        stateDict[s.stateName] = []
        for t in complementOTA.trans:
            if t.source == s.stateName:
                if t.target not in stateDict[s.stateName]:
                    stateDict[s.stateName].append(t.target)
    # 获得最短反例路径
    shortestPath = findShortestPath(stateDict, complementOTA.initState, complementOTA.errorState)
    # 计算距离度量
    if len(shortestPath) == 0:
        return 0
    else:
        ctxLength = len(shortestPath) - 1
        metric = math.pow(2, -ctxLength)
        return metric


def computeMetric(stableHpy, targetFullSys):
    mergeOTA = buildMergeOTA(stableHpy, targetFullSys)
    complementOTA = buildComplementOTA(mergeOTA)
    metric = distanceMetric(complementOTA)
    return metric


# --------------------------------- 辅助函数 ---------------------------------

# 假设下输入LTWs，获得LRTWs+value(补全)
def getHpyLTWsValue(sample, hypothesis):
    LRTWs = []
    curState = hypothesis.initState
    for ltw in sample:
        if curState == hypothesis.sinkState:
            LRTWs.append(ResetTimedWord(ltw.input, ltw.time, True))
        else:
            for tran in hypothesis.trans:
                if tran.source == curState and tran.isPass(ltw):
                    curState = tran.target
                    if tran.isReset:
                        isReset = True
                    else:
                        isReset = False
                    LRTWs.append(ResetTimedWord(ltw.input, ltw.time, isReset))
                    break
    if curState in hypothesis.acceptStates:
        value = 1
    elif curState == hypothesis.sinkState:
        value = -1
    else:
        value = 0
    return LRTWs, value


# 补全区间
def complementIntervals(guards):
    partitions = []
    key = []
    floor_bn = timeInterval.BracketNum('0', timeInterval.Bracket.LC)
    ceil_bn = timeInterval.BracketNum('+', timeInterval.Bracket.RO)
    for guard in guards:
        min_bn = guard.min_bn
        max_bn = guard.max_bn
        if min_bn not in key:
            key.append(min_bn)
        if max_bn not in key:
            key.append(max_bn)
    copyKey = copy.deepcopy(key)
    for bn in copyKey:
        complement = bn.complement()
        if complement not in copyKey:
            copyKey.append(complement)
    if floor_bn not in copyKey:
        copyKey.insert(0, floor_bn)
    if ceil_bn not in copyKey:
        copyKey.append(ceil_bn)
    copyKey.sort()
    for index in range(len(copyKey)):
        if index % 2 == 0:
            tempGuard = timeInterval.Guard(copyKey[index].getBN() + ',' + copyKey[index + 1].getBN())
            partitions.append(tempGuard)
    for g in guards:
        if g in partitions:
            partitions.remove(g)
    return partitions


# target是否在tempStates, finalStates中存在
def alreadyHas(target, tempStates, finalStates):
    for i in tempStates:
        if i.stateName == target:
            return True
    for j in finalStates:
        if j.stateName == target:
            return True
    return False


# 区间求交集
def intersectionGuard(guards1, guards2):
    guards = []
    newFlag = False
    for i in range(len(guards1)):
        for j in range(len(guards2)):
            minType1, maxType1 = guards1[i].guard.split(',')
            minType2, maxType2 = guards2[j].guard.split(',')
            minNum1 = float(minType1[1:])
            minNum2 = float(minType2[1:])
            if maxType1[:-1] == '+':
                maxNum1 = float('inf')
            else:
                maxNum1 = float(maxType1[:-1])
            if maxType2[:-1] == '+':
                maxNum2 = float('inf')
            else:
                maxNum2 = float(maxType2[:-1])
            if maxType1[:-1] == '+' and maxType2[:-1] == '+':
                if minNum1 == minNum2:
                    if minType1[0] == '(' or minType2[0] == '(':
                        newFlag = True
                        guards.append(timeInterval.Guard('(' + str(minNum1) + ',' + maxType2))
                    else:
                        newFlag = True
                        guards.append(timeInterval.Guard('[' + str(minNum1) + ',' + maxType2))
                else:
                    if minNum1 < minNum2:
                        newFlag = True
                        guards.append(timeInterval.Guard(minType2 + ',' + maxType2))
                    else:
                        newFlag = True
                        guards.append(timeInterval.Guard(minType1 + ',' + maxType2))
            elif maxNum2 < minNum1:
                pass
            elif minNum2 > maxNum1:
                pass
            elif minNum1 > minNum2 and maxNum1 < maxNum2:
                newFlag = True
                guards.append(guards1[i])
            elif minNum1 < minNum2 and maxNum1 > maxNum2:
                newFlag = True
                guards.append(guards2[j])
            elif minNum1 < minNum2 < maxNum1 < maxNum2:
                newFlag = True
                guards.append(timeInterval.Guard(minType2 + ',' + maxType1))
            elif minNum2 < minNum1 < maxNum2 < maxNum1:
                newFlag = True
                guards.append(timeInterval.Guard(minType1 + ',' + maxType2))
            elif minNum1 == minNum2 and maxNum1 != maxNum2:
                newFlag = True
                if minType1[0] == '(' or minType2[0] == '(':
                    leftType = '('
                else:
                    leftType = '['
                if maxNum1 >= maxNum2:
                    guards.append(timeInterval.Guard(leftType + str(minNum1) + ',' + maxType2))
                else:
                    guards.append(timeInterval.Guard(leftType + str(minNum1) + ',' + maxType1))
            elif minNum1 == maxNum2:
                if minType1[0] == '[' and maxType2[-1] == ']':
                    newFlag = True
                    guards.append(timeInterval.Guard('[' + str(minNum1) + ',' + str(minNum1) + ']'))
            elif minNum2 == maxNum1:
                if minType2[0] == '[' and maxType1[-1] == ']':
                    newFlag = True
                    guards.append(timeInterval.Guard('[' + str(minNum2) + ',' + str(minNum2) + ']'))
            elif maxNum1 == maxNum2 and minNum1 != minNum2:
                newFlag = True
                if maxType1[-1] == ')' or maxType2[-1] == ')':
                    rightType = ')'
                else:
                    rightType = ']'
                if minNum1 >= minNum2:
                    guards.append(timeInterval.Guard(minType1 + ',' + str(maxNum1) + rightType))
                else:
                    guards.append(timeInterval.Guard(minType2 + ',' + str(maxNum1) + rightType))
            elif minNum1 == minNum2 and maxNum1 == maxNum2:
                if maxType1[-1] == ')' or maxType2[-1] == ')':
                    rightType = ')'
                else:
                    rightType = ']'
                if minType1[0] == '(' or minType2[0] == '(':
                    leftType = '('
                else:
                    leftType = '['
                if leftType == '(' and rightType == ')':
                    if minNum1 != maxNum1:
                        newFlag = True
                        guards.append(timeInterval.Guard(leftType + str(minNum1) + ',' + str(maxNum1) + rightType))
                    else:
                        pass
                else:
                    newFlag = True
                    guards.append(timeInterval.Guard(leftType + str(minNum1) + ',' + str(maxNum1) + rightType))
    return guards, newFlag


# 找到一条从start到end的最短路径
def findShortestPath(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return path
    shortestPath = []
    for node in graph[start]:
        if node not in path:
            tempNode = node
            newPath = findShortestPath(graph, tempNode, end, path)
            if newPath:
                if not shortestPath or len(newPath) < len(shortestPath):
                    shortestPath = newPath
    return shortestPath


# 找到所有从start到end的路径
def findAllPath(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    paths = []  # 存储所有路径
    for node in graph[start]:
        if node not in path:
            tempNode = node
            newPaths = findAllPath(graph, tempNode, end, path)
            for newPath in newPaths:
                paths.append(newPath)
    return paths


# 获得状态到达集
def getStateTrace(complementOTA, shortestPath):
    trace = []
    tempPath = shortestPath[:-1]
    if len(tempPath) == 1:
        return trace, 0
    else:
        i = 0
        nowTime = 0
        while i < len(tempPath) - 1:
            for tran in complementOTA.trans:
                if tran.source == tempPath[i] and tran.target == tempPath[i + 1]:
                    time = getMinTime(tran.guards, nowTime)
                    lrtw = ResetTimedWord(tran.input, time, tran.isReset)
                    trace.append(lrtw)
                    if tran.isReset:
                        nowTime = 0
                    else:
                        nowTime = time
                    break
            i += 1
        return trace, nowTime


# 获得时间
def getMinTime(guards, nowTime):
    guards = sortGuards(guards)
    time = 0
    for guard in guards:
        minNum = guard.get_min()
        maxNum = guard.get_max()
        if nowTime <= minNum:
            if guard.get_closed_min():
                time = minNum
            else:
                time = minNum + 0.5
        elif (nowTime > maxNum) or (nowTime == maxNum and not guard.get_closed_max()):
            pass
        else:
            time = nowTime
    return time


# Guards排序
def sortGuards(guards):
    for i in range(len(guards) - 1):
        for j in range(len(guards) - i - 1):
            if guards[j].min_bn > guards[j + 1].min_bn:
                guards[j], guards[j + 1] = guards[j + 1], guards[j]
    return guards


# 获得时间List
def getTimeList(guards, nowTime):
    time = []
    guards = sortGuards(guards)
    for guard in guards:
        minNum = guard.get_min()
        maxNum = guard.get_max()
        if (nowTime > maxNum) or (nowTime == maxNum and not guard.get_closed_max()):
            pass
        elif nowTime <= minNum:
            if guard.guard[1:-1].split(',')[1] == '+':
                time.append(minNum + 0.5)
                break
            else:
                time.append((minNum + maxNum) / 2)
                break
        else:
            if guard.guard[1:-1].split(',')[1] == '+':
                time.append(nowTime + 0.5)
                break
            else:
                time.append((nowTime + maxNum) / 2)
                break
    time = normalize(time)
    return time


# 将序列都转变为0.5间隔的数
def normalize(timeList):
    result = []
    for i in timeList:
        if i == 0:
            result.append(i)
        else:
            x, y = math.modf(i)
            if x == 0:
                result.append(i)
            else:
                result.append(y + 0.5)
    return result


def getLength(elm):
    return len(elm)
