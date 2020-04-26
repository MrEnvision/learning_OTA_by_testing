import json
import timeInterval
from timedWord import ResetTimedWord, TimedWord, LRTW_to_LTW, LRTW_to_DTW


class TestResult(object):
    def __init__(self, LRTWs, result):
        self.LRTWs = LRTWs
        self.result = result


class System(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, MQs=None):
        if MQs is None:
            MQs = {}
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.MQs = MQs

    def isLTWsTested(self, trace):
        for value in self.MQs.values():
            if LRTW_to_LTW(value.LRTWs) == trace:
                return True, value.LRTWs, value.result
        else:
            return False, [], []

    def isDTWsTested(self, trace):
        for value in self.MQs.values():
            if LRTW_to_DTW(value.LRTWs) == trace:
                return True, value.LRTWs, value.result
        else:
            return False, [], []

    def addTestResult(self, LRTWs, result):
        eleId = len(self.MQs)
        self.MQs.update({eleId: TestResult(LRTWs, result)})


class SysTran(object):
    def __init__(self, tranId, source, input, guards, isReset, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.guards = guards
        self.isReset = isReset
        self.target = target

    def isPass(self, tw):
        if tw.input == self.input:
            for guard in self.guards:
                if guard.isInInterval(tw.time):
                    return True
        return False

    def showGuards(self):
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


# 构建系统
def buildSystem(jsonFile):
    with open(jsonFile, 'r') as f:
        # 文件数据获取
        data = json.load(f)
        inputs = data["inputs"]
        states = data["states"]
        trans = data["trans"]
        initState = data["initState"]
        acceptStates = data["acceptStates"]
    # trans 处理
    transSet = []
    for tran in trans:
        tranId = str(tran)
        source = trans[tran][0]
        target = trans[tran][4]
        input = trans[tran][1]
        # 重置信息
        resetTemp = trans[tran][3]
        isReset = False
        if resetTemp == "r":
            isReset = True
        # 时间处理 - guard
        intervalsStr = trans[tran][2]
        intervalsList = intervalsStr.split('U')
        guards = []
        for guard in intervalsList:
            newGuard = timeInterval.Guard(guard.strip())
            guards.append(newGuard)
        systemTran = SysTran(tranId, source, input, guards, isReset, target)
        transSet += [systemTran]
    transSet.sort(key=lambda x: x.tranId)
    system = System(inputs, states, transSet, initState, acceptStates)
    return system


# 系统交互 - 输入DTWs，输出DRTWs和value（DRTWs补全）- 用于delay-timed test
def systemOutput(DTWs, targetSys):
    DRTWs = []
    value = []
    nowTime = 0
    curState = targetSys.initState
    for dtw in DTWs:
        if curState == "Error":
            DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
            value = -1
        else:
            time = dtw.time + nowTime
            newLTW = TimedWord(dtw.input, time)
            flag = False
            for tran in targetSys.trans:
                if tran.source == curState and tran.isPass(newLTW):
                    flag = True
                    curState = tran.target
                    if tran.isReset:
                        nowTime = 0
                        isReset = True
                    else:
                        nowTime = time
                        isReset = False
                    DRTWs.append(ResetTimedWord(dtw.input, dtw.time, isReset))
                    break
            if not flag:
                DRTWs.append(ResetTimedWord(dtw.input, dtw.time, True))
                value = -1
                curState = "Error"
    if curState in targetSys.acceptStates:
        value = 1
    elif curState != 'Error':
        value = 0
    return DRTWs, value


# 系统交互 - 输入单个DTW，输出当前状态和value - 用于logical-timed test
def systemTest(DTW, nowTime, curState, targetSys):
    value = None
    resetFlag = False  # 重置信号
    tranFlag = False  # tranFlag为true表示有这样的迁移
    if DTW is None:
        if curState in targetSys.acceptStates:
            value = 1
        else:
            value = 0
    else:
        LTW = TimedWord(DTW.input, DTW.time + nowTime)
        for tran in targetSys.trans:
            if tran.source == curState and tran.isPass(LTW):
                tranFlag = True
                curState = tran.target
                if tran.isReset:
                    resetFlag = True
                break
        if not tranFlag:
            value = -1
            curState = 'Error'
            resetFlag = True
        if curState in targetSys.acceptStates:
            value = 1
        elif curState != 'Error':
            value = 0
    return curState, value, resetFlag
