import sys
import json
import time
from learner import learnOTA
from system import buildSystem
from makePic import makeOTA, makeLearnedOTA
from error import getError


def main():
    ### 构建目标系统
    # targetSys = buildSystem(modelFile)
    # makeOTA(targetSys, '.', '/results/targetSys')
    targetSys = buildSystem(filePath + "/example.json")
    makeOTA(targetSys, filePath, '/results/目标系统')

    ### 获取前提条件
    # with open(preFile, 'r') as f:
    with open(filePath + '/precondition.json', 'r') as f:
        # 文件数据获取
        custom = json.load(f)
        inputs = custom["inputs"]  # input字母表
        upperGuard = custom["upperGuard"]  # 时间上界
        epsilon = custom["epsilon"]  # 准确度
        delta = custom["delta"]  # 置信度
        stateNum = custom["stateNum"]  # 状态数(含sink状态) - 主要用于分布的实现，实际可以不需要

    ### 学习OTA
    startLearning = time.time()
    # learner
    learnedSys, mqNum, eqNum, testNum, metric = learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum)
    passingRate = getError(learnedSys, targetSys, upperGuard, stateNum)
    endLearning = time.time()

    ### 学习结果
    if learnedSys is None:
        print("Error! Learning Failed.")
        return {"Data": "Failed"}
    else:
        print("---------------------------------------------------")
        print("Succeed! The learned OTA is as follows.")
        makeLearnedOTA(learnedSys, '.', '/results/learnedSys')
        print("---------------------------------------------------")
        print("learning time: " + str(endLearning - startLearning))
        print("mqNum: " + str(mqNum))
        print("eqNum: " + str(eqNum))
        print("testNum: " + str(testNum))
        # print("当前距离: " + str(metric))
        print('accuracy', str(1 - epsilon), ' passingRate', str(passingRate))
        resultObj = {
            "Data": "Success",
            "time": endLearning - startLearning,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum,
            "metric": metric
        }
        return resultObj


if __name__ == '__main__':
    # paras = sys.argv
    # modelFile = paras[1]
    # preFile = paras[2]
    # # 实验次数
    # testTime = 1
    # # 实验结果
    # data = {}
    # for i in range(testTime):
    #     print("Now: ", i)
    #     result = main()
    #     data.update({i: result})
    # json_str = json.dumps(data, indent=2)
    # with open("results/result_1.json", 'w') as json_file:
    #     json_file.write(json_str)

    # 目标模型
    # filePath = "Automata/experiment_state/5_2_5_2-1"
    filePath = "Automata/TCP"
    # 实验次数
    testTime = 8
    # 实验结果
    data = {}
    for i in range(testTime):
        print("Now: ", i)
        result = main()
        data.update({i: result})
    json_str = json.dumps(data, indent=2)
    with open(filePath + "/result_1.json", 'w') as json_file:
        json_file.write(json_str)
