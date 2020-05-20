import json
from numpy import *


def main():
    jsonFile = 'Experiments/TCP/result.json'
    with open(jsonFile, 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data = list(data.values())

    mq = []
    eq = []
    tests = []
    states = []
    learningTime = []
    passingRate = []
    correct = 0
    for i in data:
        mq.append(i['mqNum'])
        eq.append(i['eqNum'])
        tests.append(i['testNum'])
        states.append(len(i['Model']['states']) - 1)
        learningTime.append(i['learningTime'])
        passingRate.append(i['passingRate'])
        if i['correct']:
            correct += 1

    print(min(mq))
    print(max(mq))
    print(mean(mq))
    print(min(eq))
    print(max(eq))
    print(mean(eq))
    print(min(tests))
    print(max(tests))
    print(mean(tests))
    print(mean(states))
    print(correct)
    print(mean(learningTime))
    print(mean(passingRate))


if __name__ == '__main__':
    main()
