import sys
import random
import json
import time
from system import buildSystem
from makePic import makeOTA
from normalLearning.learner import learnOTA
from normalLearning.hypothesis import remove_sinklocation
from normalLearning.validate import validate
from normalLearning.ota import buildOTA


def main():
    # build target system
    targetSys = buildOTA(modelFile, 's')
    makeOTA(buildSystem(modelFile), filePath, '/results/targetSys')

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
    print("********** start learning *************")
    flag, learnedSys, mqNumCache, mqNum, eqNumCache, eqNum, tableNum = learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum, debug_flag=False)
    endLearning = time.time()

    if flag:
        # verify model quality
        correctFlag, passingRate = validate(learnedSys, targetSys, upperGuard, stateNum)

        target_without_sink = remove_sinklocation(learnedSys)
        print("The learned One-clock Timed Automata: ")
        target_without_sink.show()

        print("---------------------------------------------------")
        print("Succeed! The results are as follows.")
        print("Total time of learning: " + str(endLearning - startLearning))
        print("Total number of membership query: " + str(mqNumCache))
        print("Total number of membership query (no-cache): " + str(mqNum))
        print("Total number of equivalence query: " + str(eqNumCache))
        print("Total number of equivalence query (no-cache): " + str(eqNum))
        print("Total number of tables explored: " + str(tableNum))
        if correctFlag:
            print("Completely correct!")
        else:
            print('accuracy', str(1 - epsilon), ' passingRate', str(passingRate))

        trans = []
        for t in target_without_sink.trans:
            trans.append([str(t.id), str(t.source), str(t.label), t.show_constraints(), str(t.reset), str(t.target)])
        states = []
        for s in target_without_sink.locations:
            states.append(s.name)

        resultObj = {
            "result": "Success",
            "learningTime": endLearning - startLearning,
            "mqNumCache": mqNumCache,
            "mqNum": mqNum,
            "eqNumCache": eqNumCache,
            "eqNum": eqNum,
            "tableNum": tableNum,
            "passingRate": passingRate,
            "correct": correctFlag,
            "Model": {
                "inputs": target_without_sink.sigma,
                "states": states,
                "initState": target_without_sink.initstate_name,
                "acceptStates": target_without_sink.accept_names,
                "trans": trans
            }
        }
        return resultObj
    else:
        print("---------------------------------------------------")
        print("Error! Learning Failed.")
        return {"result": "Failed"}


if __name__ == '__main__':
    # used to reproduce experimental results
    random.seed(1)

    # # file directory
    # filePath = "Automata/3_2_10"
    filePath = sys.argv[1]
    # target model file
    modelFile = filePath + "/model.json"
    # prior information required for learning
    preconditionFile = filePath + "/precondition.json"

    # number of experiments
    experimentNum = 1
    # Start of experiment
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
