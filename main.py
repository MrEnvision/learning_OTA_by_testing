import json
import time
from system import buildSystem
from learner import learnOTA
from makePic import makeOTA, makeLearnedOTA
from validate import validate
from hypothesis import structSimpleHypothesis


def main():
    # build target system
    targetSys = buildSystem(modelFile)
    makeOTA(targetSys, filePath, '/results/目标系统')

    # get prior information required for learning
    with open(preconditionFile, 'r') as fr:
        information = json.load(fr)
        inputs = information["inputs"]
        upperGuard = information["upperGuard"]
        epsilon = information["epsilon"]  # accuracy
        delta = information["delta"]  # confidence
        stateNum = information["stateNum"]

    # pac learning OTA
    startLearning = time.time()
    learnedSys, mqNum, eqNum, testNum = learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum, debugFlag=False)
    passingRate = validate(learnedSys, targetSys, upperGuard, stateNum, testNum)
    endLearning = time.time()

    # learning result
    if learnedSys is None:
        print("Error! Learning Failed.")
        return {"result": "Failed"}
    else:
        print("---------------------------------------------------")
        print("Learning Succeed! The result is as follows.")
        learnedSys = structSimpleHypothesis(learnedSys)
        makeLearnedOTA(learnedSys, filePath, '/results/learnedSys' + str(i))
        print("Total time of learning: " + str(endLearning - startLearning))
        print("Total number of MQs (no-cache): " + str(mqNum))
        print("Total number of EQs (no-cache): " + str(eqNum))
        print("Total number of test (no-cache): " + str(testNum))
        print('accuracy', str(1 - epsilon), ' passingRate', str(passingRate))
        resultObj = {
            "result": "Success",
            "time": endLearning - startLearning,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum,
            "passingRate": passingRate
        }
        return resultObj


if __name__ == '__main__':
    # file directory
    filePath = "Automata/TCP"
    # target model file
    modelFile = filePath + "/example.json"
    # prior information required for learning
    preconditionFile = filePath + "/precondition.json"
    # number of experiments
    experimentNum = 1
    with open(filePath + "/result.json", 'w') as f:
        json.dump({}, f)
    for i in range(experimentNum):
        print("Now experiment: ", i)
        result = main()
        with open(filePath + "/result.json", 'r') as jsonFile:
            data = json.load(jsonFile)
            data[str(i + 1)] = result
        with open(filePath + "/result.json", 'w') as jsonFile:
            jsonFile.write(json.dumps(data, indent=2))
