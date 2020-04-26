import json
import time
from learner import learnOTA
from system import buildSystem
from makePic import makeOTA, makeLearnedOTA


def main():
    ### 构建目标系统
    targetSys = buildSystem(filePath + "/example.json")
    # makeOTA(targetSys, filePath, '/results/目标系统')

    ### 获取前提条件
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
    learnedSys, mqNum, eqNum, testNum, error = learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum)
    endLearning = time.time()

    ### 学习结果
    if learnedSys is None:
        print("Error! Learning Failed.")
        return {"Data": "Failed"}
    else:
        print("---------------------------------------------------")
        print("Succeed! The learned OTA is as follows.")
        makeLearnedOTA(learnedSys, filePath, '/results/猜想系统_' + str(i))
        print("---------------------------------------------------")
        print("学习总时间: " + str(endLearning - startLearning))
        print("成员查询数量: " + str(mqNum))
        print("等价查询数量: " + str(eqNum))
        print("测试数量: " + str(testNum))
        print("误差: " + str(error))
        resultObj = {
            "Data": "Success",
            "time": endLearning - startLearning,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum,
            "error": error
        }
        return resultObj


if __name__ == '__main__':
    # 目标模型
    filePath = "Automata/TCP"
    # 实验次数
    testTime = 5
    # 实验结果
    data = {}
    for i in range(testTime):
        print("Now: ", i)
        result = main()
        data.update({i: result})
    jsonStr = json.dumps(data, indent=2)
    with open(filePath + "/result.json", 'w') as json_file:
        json_file.write(jsonStr)
