import json


def main():
    jsonFile = 'test_8_16/result_2.json'
    with open(jsonFile, 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data = list(data.values())
    for i in data:
        print(i['time'])
    print("_________________")
    for i in data:
        print(i['mqNum'])
    print("_________________")
    for i in data:
        print(i['eqNum'])
    print("_________________")
    for i in data:
        print(i['testNum'])


if __name__ == '__main__':
    main()
