import copy
import obsTable
from teacher import EQs
from hypothesis import structDiscreteOTA, structHypothesisOTA
from comparator import hpyCompare, buildCanonicalOTA
from error import computeError


def learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum):
    mqNum = 0  # 成员查询数
    eqNum = 0  # 等价查询数
    testNum = 0  # 测试次数

    # 目标系统补全
    tempSys = copy.deepcopy(targetSys)
    targetFullSys = buildCanonicalOTA(tempSys)

    ### 初始化Table
    table, mqNum = obsTable.initTable(inputs, targetSys, mqNum)
    print("***************** init-Table_1 is as follow *******************")
    table.show()

    ### 迭代学习
    equivalent = False
    stableHpy = None  # 学习所得系统
    tNum = 1  # 观察表数
    metric = 1  # 初始距离为1

    while not equivalent:
        # 属性验证
        prepared = obsTable.isPrepared(table)
        while not prepared:
            # 处理closed
            flagClosed, closedMove = obsTable.isClosed(table)
            if not flagClosed:
                table, mqNum = obsTable.makeClosed(table, inputs, closedMove, targetSys, mqNum)
                tNum = tNum + 1
                print("***************** closed-Table_" + str(tNum) + " is as follow *******************")
                table.show()
            # 处理consistent
            flagConsistent, consistentAdd = obsTable.isConsistent(table)
            if not flagConsistent:
                table, mqNum = obsTable.makeConsistent(table, consistentAdd, targetSys, mqNum)
                tNum = tNum + 1
                print("***************** consistent-Table_" + str(tNum) + " is as follow *******************")
                table.show()
            prepared = obsTable.isPrepared(table)

        ### OTA构建
        # 迁移为时间点的OTA
        discreteOTA = structDiscreteOTA(table, inputs)
        print("***************** discreteOTA_" + str(eqNum + 1) + " is as follow. *******************")
        discreteOTA.showDiscreteOTA()
        # 迁移为时间区间的OTA
        hypothesisOTA = structHypothesisOTA(discreteOTA)
        print("***************** Hypothesis_" + str(eqNum + 1) + " is as follow. *******************")
        hypothesisOTA.showOTA()

        # # 无比较器版本
        # stableHpy = copy.deepcopy(hypothesisOTA)
        # ### 等价测试
        # equivalent, ctx, testNum, error = EQs(hypothesisOTA, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum)
        # eqNum = eqNum + 1

        # 比较器版本
        flag, ctx, mqNum, metric = hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, targetFullSys, mqNum, metric)
        if flag:
            ### 等价测试
            equivalent, ctx, testNum = EQs(hypothesisOTA, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum)
            eqNum = eqNum + 1
            stableHpy = copy.deepcopy(hypothesisOTA)
        else:
            print("Comparator找到反例！！！")
            equivalent = False

        if not equivalent:
            # 反例显示
            print("***************** counterexample is as follow. *******************")
            print([lrtw.show() for lrtw in ctx])
            # 反例处理
            table, mqNum = obsTable.dealCtx(table, ctx, targetSys, mqNum)
            tNum = tNum + 1
            print("***************** New-Table" + str(tNum) + " is as follow *******************")
            table.show()
    error = computeError(stableHpy, targetFullSys, upperGuard)
    return stableHpy, mqNum, eqNum, testNum, error
