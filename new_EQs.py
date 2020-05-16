import math
import copy
import random
from tester import testDTWs
from timedWord import TimedWord, DRTW_to_LRTW, LRTW_to_LTW
from teacher import getHpyDTWsValue
# import makePic


def min_constraint_double(c):
    """
        Get the double of the minimal number in an interval.
        1. if the interval is empty, return None
        2. if [a, b$, return "2 * a".
        3. if (a, b$, return "2 * a + 1".
    """
    if c.isEmpty():
        return None
    if c.closed_min == True:
        return 2 * int(float(c.min_value))
    else:
        return 2 * int(float(c.min_value)) + 1


def max_constraint_double(c, upperGuard):
    """
        Get the double of the maximal number in an interval.
        1. if the interval is empty, return None
        2. if $a, b], return "2 * b".
        3. if $a, b), return "2 * b - 1".
        4. if $a, +), return "2 * upperGuard + 1".
    """
    if c.isEmpty():
        return None
    if c.closed_max:
        return 2 * int(float(c.max_value))
    elif c.max_value == '+':
        return 2 * upperGuard + 1
    else:
        return 2 * int(float(c.max_value)) - 1


def sampleDistribution(distr):
    s = sum(distr)
    if s == 0:
        return None
    a = random.randint(0, s - 1)

    for i, n in enumerate(distr):
        if n > a:
            return i
        else:
            a -= n


def minimizeCounterexample(teacher, hypothesis, sample):
    """Minimize a given delay-timed word."""
    reset = []
    current_state = hypothesis.initState
    current_clock = 0
    ltw = []

    # Fix computation with 0.1
    def round1(x):
        return int(x * 10 + 0.5) / 10

    def one_lower(x):
        if round1(x - int(x)) == 0.1:
            return int(x)
        else:
            return round1(x - 0.9)

    # Find sequence of reset information
    realDRTWs, realValue = testDTWs(sample, teacher)
    ltw = LRTW_to_LTW(DRTW_to_LRTW(realDRTWs))
    for i in realDRTWs:
        reset.append(i.isReset)
    # for tw in sample:
    #     current_clock = round1(current_clock + tw.time)
    #     ltw.append(TimedWord(tw.input, current_clock))
    #     for tran in hypothesis.trans:
    #         found = False
    #         if current_state == tran.source and tran.isPass(TimedWord(tw.input, current_clock)):
    #             reset.append(tran.isReset)
    #             current_state = tran.target
    #             if tran.isReset:
    #                 current_clock = 0
    #             found = True
    #             break
    #     assert found

    def normalize(trace):
        newTrace = []
        for i in trace:
            if math.modf(float(i.time))[0] == 0.0:
                time = math.modf(float(i.time))[1]
            else:
                time = math.modf(float(i.time))[1] + 0.1
            newTrace.append(TimedWord(i.input, time))
        return newTrace

    ltw = normalize(ltw)

    # print('ltw:', [i.show() for i in ltw])
    def ltw_to_dtw(ltw):
        dtw = []
        for i in range(len(ltw)):
            if i == 0 or reset[i - 1]:
                dtw.append(TimedWord(ltw[i].input, ltw[i].time))
            else:
                dtw.append(TimedWord(ltw[i].input, round1(ltw[i].time - ltw[i - 1].time)))
        return dtw

    # print('initial:', [i.show() for i in ltw_to_dtw(ltw)])

    for i in range(len(ltw)):
        while True:
            if i == 0 or reset[i - 1]:
                can_reduce = (ltw[i].time > 0)
            else:
                can_reduce = (ltw[i].time > ltw[i - 1].time)
            if not can_reduce:
                break
            ltw2 = copy.deepcopy(ltw)
            ltw2[i] = TimedWord(ltw[i].input, one_lower(ltw[i].time))
            if not isCounterexample(teacher, hypothesis, ltw_to_dtw(ltw2)):
                break
            ltw = copy.deepcopy(ltw2)

    # print('final:', [i.show() for i in ltw_to_dtw(ltw)])
    return ltw_to_dtw(ltw)


def isCounterexample(teacher, hypothesis, sample):
    """Compare evaluation of teacher and hypothesis on the given sample
    (a delay-timed word).

    """
    # Evaluation of sample on the teacher, should be -1, 0, 1
    realDRTWs, realValue = testDTWs(sample, teacher)

    # Evaluation of sample on the hypothesis, should be -1, 0, 1
    DRTWs, value = getHpyDTWsValue(sample, hypothesis)
    if realValue == -1:
        if realValue == -1 and value == 1:
            return True
        else:
            return False
    elif (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
        return True
    else:
        return False
    # return value == realValue


def sampleGeneration(inputs, upperGuard, stateNum, length=None):
    """Generate a sample."""
    sample = []
    if length is None:
        length = random.randint(1, stateNum)
    for i in range(length):
        input = inputs[random.randint(0, len(inputs) - 1)]
        time = random.randint(0, upperGuard * 3 + 1)
        if time % 2 == 0:
            time = time // 2
        else:
            time = time // 2 + 0.1
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


def sampleGeneration_valid(teacher, upperGuard, length):
    """Generate a sample adapted to the given teacher."""
    # First produce a path (as a list of transitions) in the OTA
    path = []
    current_state = teacher.initState
    for i in range(length):
        edges = []
        for tran in teacher.trans:
            if current_state == tran.source:
                edges.append(tran)
        edge = random.choice(edges)
        path.append(edge)
        current_state = edge.target

    # Next, figure out (double of) the minimum and maximum logical time.
    min_time, max_time = [], []
    for tran in path:
        assert len(tran.guards) == 1
        min_time.append(min_constraint_double(tran.guards[0]))
        max_time.append(max_constraint_double(tran.guards[0], upperGuard))

    # For each transition, maintain a mapping from logical time to the
    # number of choices.
    weight = dict()
    for i in reversed(range(length)):
        tran = path[i]
        mn, mx = min_time[i], max_time[i]
        weight[i] = dict()
        if i == length - 1 or tran.isReset:
            for j in range(mn, mx + 1):
                weight[i][j] = 1
        else:
            for j in range(mn, mx + 1):
                weight[i][j] = 0
                for k, w in weight[i + 1].items():
                    if k >= j:
                        weight[i][j] += w

    # Now sample according to the weights
    double_times = []
    cur_time = 0
    for i in range(length):
        start_time = max(min_time[i], cur_time)
        distr = []
        for j in range(start_time, max_time[i] + 1):
            distr.append(weight[i][j])
        if sum(distr) == 0:
            return None  # sampling failed
        cur_time = sampleDistribution(distr) + start_time
        double_times.append(cur_time)
        if path[i].isReset:
            cur_time = 0

    # Finally, change doubled time to fractions.
    ltw = []
    for i in range(length):
        if double_times[i] % 2 == 0:
            time = double_times[i] // 2
        else:
            time = double_times[i] // 2 + 0.1
        ltw.append(TimedWord(path[i].input, time))

    # Convert logical-timed word to delayed-timed word.
    dtw = []
    for i in range(length):
        if i == 0 or path[i - 1].isReset:
            dtw.append(TimedWord(path[i].input, ltw[i].time))
        else:
            dtw.append(TimedWord(path[i].input, ltw[i].time - ltw[i - 1].time))

    return dtw


def sampleGeneration_invalid(teacher, upperGuard, length):
    assert length > 0
    sample_prefix = None
    while sample_prefix is None:
        # sample_prefix = sampleGeneration_valid(teacher, upperGuard, length-1)
        sample_prefix = sampleGeneration_valid(teacher, upperGuard, length)
    action = random.choice(teacher.inputs)
    time = random.randint(0, upperGuard * 3 + 1)
    if time % 2 == 0:
        time = time // 2
    else:
        time = time // 2 + 0.1
    index = random.randint(0, len(sample_prefix) - 1)
    sample_prefix[index] = TimedWord(action, time)
    return sample_prefix
    # return sample_prefix + [TimedWord(action, time)]


def sampleGeneration2(teacher, upperGuard, length):
    if random.randint(0, 1) == 0:
        return sampleGeneration_invalid(teacher, upperGuard, length)
    else:
        sample = None
        while sample is None:
            sample = sampleGeneration_valid(teacher, upperGuard, length)
        return sample


def EQs(hypothesis, upperGuard, epsilon, delta, stateNum, targetSys, eqNum, testNum):
    testSum = int((math.log(1 / delta) + math.log(2) * (eqNum + 1)) / epsilon)
    # print(testNum)
    for length in range(1, math.ceil(stateNum * 1.5)):
        ctx = None
        correct = 0
        i = 0
        # print(length)
        while i < testSum // stateNum:
            i += 1
            testNum += 1
            # Generate sample (delay-timed word) according to fixed distribution
            # sample = sampleGeneration(hypothesis.sigma, upperGuard, stateNum, length=length)
            sample = sampleGeneration2(targetSys, upperGuard, length)

            # Compare the results
            if isCounterexample(targetSys, hypothesis, sample):
                if ctx is None or sample < ctx:
                    ctx = sample

        if ctx is not None:
            # print('init ctx:', [i.show() for i in ctx])

            # print('--------------init---------------')
            # print([i.show() for i in ctx])
            # realDRTWs, realValue = testDTWs(ctx, targetSys)
            # DRTWs, value = getHpyDTWsValue(ctx, hypothesis)
            # print(realValue, value)
            # tempCtx = copy.deepcopy(ctx)

            ctx = minimizeCounterexample(targetSys, hypothesis, ctx)

            # print('--------------update---------------')
            # print([i.show() for i in ctx])
            # realDRTWs, realValue = testDTWs(ctx, targetSys)
            # DRTWs, value = getHpyDTWsValue(ctx, hypothesis)
            # if realValue == value:
            #     print(realValue, value)
            #     makePic.makeLearnedOTA(hypothesis, '', 'results/learnedSys')
            #     makePic.makeOTA(targetSys, '', 'results/目标系统')
            #     tempCtx = minimizeCounterexample(targetSys, hypothesis, tempCtx)
            # print(realValue, value)
            realDRTWs, realValue = testDTWs(ctx, targetSys)
            return False, realDRTWs, testNum
    return True, None, testNum
