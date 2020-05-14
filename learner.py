import copy
import obsTable
from teacher import EQs
from hypothesis import structDiscreteOTA, structHypothesisOTA
import equiv.equiv_wrapper as equiv_wrapper


def learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum, debugFlag):
    mqNum = 0  # number of MQs
    eqNum = 0  # number of EQs
    testNum = 0  # number of tests

    ### init Table
    table, mqNum = obsTable.initTable(inputs, targetSys, mqNum)
    if debugFlag:
        print("***************** init-Table_1 is as follow *******************")
        table.show()

    ### learning start
    equivalent = False
    stableHpy = None  # learned model
    tNum = 1  # number of table

    while not equivalent:
        prepared = obsTable.isPrepared(table)
        while not prepared:
            # make closed
            flagClosed, closedMove = obsTable.isClosed(table)
            if not flagClosed:
                table, mqNum = obsTable.makeClosed(table, inputs, closedMove, targetSys, mqNum)
                tNum = tNum + 1
                if debugFlag:
                    print("***************** closed-Table_" + str(tNum) + " is as follow *******************")
                    table.show()
            # make consistent
            flagConsistent, consistentAdd = obsTable.isConsistent(table)
            if not flagConsistent:
                table, mqNum = obsTable.makeConsistent(table, consistentAdd, targetSys, mqNum)
                tNum = tNum + 1
                if debugFlag:
                    print("***************** consistent-Table_" + str(tNum) + " is as follow *******************")
                    table.show()
            prepared = obsTable.isPrepared(table)

        ### build hypothesis
        # 迁移为时间点的OTA
        discreteOTA = structDiscreteOTA(table, inputs)
        if debugFlag:
            print("***************** discreteOTA_" + str(eqNum + 1) + " is as follow. *******************")
            discreteOTA.showDiscreteOTA()
        # 迁移为时间区间的OTA
        hypothesisOTA = structHypothesisOTA(discreteOTA)
        if debugFlag:
            print("***************** Hypothesis_" + str(eqNum + 1) + " is as follow. *******************")
            hypothesisOTA.showOTA()

        ### comparator
        flag, ctx, mqNum = equiv_wrapper.hpyCompare(stableHpy, hypothesisOTA, upperGuard, targetSys, mqNum)
        if flag:
            ### EQs
            equivalent, ctx, testNum = EQs(hypothesisOTA, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum)
            eqNum = eqNum + 1
            stableHpy = copy.deepcopy(hypothesisOTA)
        else:
            if debugFlag:
                print("Comparator找到反例！！！")
            equivalent = False

        if not equivalent:
            # show ctx
            print("***************** counterexample is as follow. *******************")
            print([drtw.show() for drtw in ctx])
            # deal with ctx
            table, mqNum = obsTable.dealCtx(table, ctx, targetSys, mqNum)
            tNum = tNum + 1
            if debugFlag:
                print("***************** New-Table" + str(tNum) + " is as follow *******************")
                table.show()
    return stableHpy, mqNum, eqNum, testNum
