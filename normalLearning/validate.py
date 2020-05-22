from comparator.equivalence import equivalence_query_normal
from normalLearning.pac_equiv import sampleGeneration


def validate(hypothesis, teacher, upperGuard, stateNum):
    inputs = teacher.sigma
    flag = False

    equivalent, _ = equivalence_query_normal(upperGuard, teacher, hypothesis)
    if equivalent:
        flag = True
        # print("Completely correct!")
        return flag, 1.0
    else:
        correct = 0
        for i in range(20000):
            sample = sampleGeneration(inputs, upperGuard, stateNum)
            realValue = teacher.is_accepted_delay(sample.tws)
            value = hypothesis.is_accepted_delay(sample.tws)
            if (realValue == 1 and value == 1) or (realValue != 1 and value != 1):
                correct += 1
        ratio = correct / 20000
        return flag, ratio
