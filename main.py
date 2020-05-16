import json
import time
import random
from system import buildSystem
from learner import learnOTA
from makePic import makeOTA, makeLearnedOTA
from validate import validate
from hypothesis import structSimpleHypothesis


def main():
    # build target system
    targetSys = buildSystem(modelFile)
    # makeOTA(targetSys, filePath, '/results/目标系统')

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
    endLearning = time.time()

    startValidating = time.time()
    correctFlag, passingRate = validate(learnedSys, targetSys, upperGuard, stateNum, eqNum, delta, epsilon)
    endValidating = time.time()

    # learning result
    if learnedSys is None:
        print("Error! Learning Failed.")
        return {"result": "Failed"}
    else:
        print("---------------------------------------------------")
        print("Learning Succeed! The result is as follows.")
        learnedSys = structSimpleHypothesis(learnedSys)
        # makeLearnedOTA(learnedSys, filePath, '/results/learnedSys' + str(i))
        print("Total time of learning: " + str(endLearning - startLearning))
        print("Total number of MQs (no-cache): " + str(mqNum))
        print("Total number of EQs (no-cache): " + str(eqNum))
        print("Total number of test (no-cache): " + str(testNum))
        print('accuracy', str(1 - epsilon), ' passingRate', str(passingRate))
        trans = []
        for t in learnedSys.trans:
            trans.append([str(t.tranId), str(t.source), str(t.input), t.showGuards(), str(t.isReset), str(t.target)])

        resultObj = {
            "result": "Success",
            "learningTime": endLearning - startLearning,
            "validatingTime": endValidating - startValidating,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum,
            "passingRate": passingRate,
            "correct": correctFlag,
            "learnedState": len(learnedSys.states),
            "Model": {
                "inputs": learnedSys.inputs,
                "states": learnedSys.states,
                "initState": learnedSys.initState,
                "acceptStates": learnedSys.acceptStates,
                "sinkState": learnedSys.sinkState,
                "trans": trans
            }
        }
        return resultObj


if __name__ == '__main__':
    random.seed(2)
    # file directory
    filePath = "Experiments/7_2_10-1"
    # target model file
    modelFile = filePath + "/7_2_10.json"
    # prior information required for learning
    preconditionFile = filePath + "/precondition.json"
    # number of experiments
    experimentNum = 10
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
