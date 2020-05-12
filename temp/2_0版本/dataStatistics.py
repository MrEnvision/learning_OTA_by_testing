import json


def main():
    jsonFile = 'Automata/experiment_2/4_3_24_10/result_2.json'
    with open(jsonFile, 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data = list(data.values())
    mqSum = eqSum = testSum = 0
    for i in data:
        mqSum += i['mqNum']
    print('mqNum', mqSum / len(data))
    for i in data:
        eqSum += i['eqNum']
    print('eqNum', eqSum / len(data))
    for i in data:
        testSum += i['testNum']
    print('testNum', testSum / len(data))


if __name__ == '__main__':
    main()
