import json
from numpy import *


def main():
    jsonFile = 'Experiments/4_4_20-1/result.json'
    with open(jsonFile, 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data = list(data.values())

    mq = []
    eq = []
    test = []
    states = []
    learningTime = []
    validatingTime = []
    passingRate = []
    correct = 0
    for i in data:
        mq.append(i['mqNum'])
        eq.append(i['eqNum'])
        test.append(i['testNum'])
        states.append(len(i['Model']['states']) - 1)
        learningTime.append(i['learningTime'])
        validatingTime.append(i['validatingTime'])
        passingRate.append(i['passingRate'])
        if i['correct']:
            correct += 1

    print(min(mq))
    print(max(mq))
    print(mean(mq))
    print(min(eq))
    print(max(eq))
    print(mean(eq))
    print(min(test))
    print(max(test))
    print(mean(test))
    print(mean(states))
    print(correct)
    print(mean(learningTime))
    print(mean(validatingTime))
    print(mean(passingRate))


if __name__ == '__main__':
    main()
