import json


def main():
    jsonFile = 'Automata/experiment_state/5_2_5_2-1/result_2.json'
    with open(jsonFile, 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data = list(data.values())
    # print('————————————mqNum————————————')
    # for i in data:
    #     print(i['mqNum'])
    # print('————————————eqNum————————————')
    # for i in data:
    #     print(i['eqNum'])
    # print('————————————testNum————————————')
    # for i in data:
    #     print(i['testNum'])
    # print('————————————passingRate————————————')
    # for i in data:
    #     print(i['passingRate'])
    mqSum = eqSum = testSum = passingRate = 0
    for i in data:
        mqSum += i['mqNum']
    print('mqNum', mqSum / len(data))
    for i in data:
        eqSum += i['eqNum']
    print('eqNum', eqSum / len(data))
    for i in data:
        testSum += i['testNum']
    print('testNum', testSum / len(data))
    for i in data:
        passingRate += i['passingRate']
    print('passingRate', passingRate / len(data))


if __name__ == '__main__':
    main()
