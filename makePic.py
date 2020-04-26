from graphviz import Digraph


# 目标系统OTA - accept
def makeOTA(data, filePath, fileName):
    dot = Digraph()
    for state in data.states:
        if state in data.acceptStates:
            dot.node(name=str(state), label=str(state), shape='doublecircle')
        else:
            dot.node(name=str(state), label=str(state))
    for tran in data.trans:
        tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
        dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 猜想OTA - accept
def makeLearnedOTA(data, filePath, fileName):
    dot = Digraph()
    states = []
    for state in data.states:
        if state != data.sinkState:
            states.append(state)
    for s in states:
        if s in data.acceptStates:
            dot.node(name=str(s), label=str(s), shape='doublecircle')
        else:
            dot.node(name=str(s), label=str(s))
    for tran in data.trans:
        if tran.source != data.sinkState and tran.target != data.sinkState:
            tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
            dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 补全OTA - accept+sink
def makeFullOTA(data, filePath, fileName):
    dot = Digraph()
    for s in data.states:
        if s in data.acceptStates:
            dot.node(name=str(s), label=str(s), shape='doublecircle')
        elif s == data.sinkState:
            dot.node(name=str(s), label=str(s), shape='diamond')
        else:
            dot.node(name=str(s), label=str(s))
    for tran in data.trans:
        tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
        dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 两个自动机的交集OTA - accept+sink
def makeMergeOTA(data, filePath, fileName):
    dot = Digraph()
    for state in data.states:
        if state.stateName in data.acceptStates:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='doublecircle')
        elif state.stateName == data.sinkState:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='diamond')
        else:
            dot.node(name=str(state.stateName), label=str(state.stateName))
    for tran in data.trans:
        tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
        dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 两个自动机的交集OTA - accept+sink
def makeMergeOTA1(data, filePath, fileName):
    dot = Digraph()
    for state in data.states:
        if state.stateName in data.acceptStates:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='doublecircle')
        elif state.stateName == data.sinkState:
            pass
        else:
            dot.node(name=str(state.stateName), label=str(state.stateName))
    for tran in data.trans:
        if tran.source != data.sinkState and tran.target != data.sinkState:
            tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
            dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 交集OTA的补 - accept+sink+error
def makeComplementOTA(data, filePath, fileName):
    dot = Digraph()
    for state in data.states:
        if state.stateName in data.acceptStates:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='doublecircle')
        elif state.stateName == data.sinkState:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='diamond')
        elif state.stateName == data.errorState:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='box')
        else:
            dot.node(name=str(state.stateName), label=str(state.stateName))
    for tran in data.trans:
        tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
        dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)


# 交集OTA的补 - accept+error
def makeComplementOTA1(data, filePath, fileName):
    dot = Digraph()
    for state in data.states:
        if state.stateName in data.acceptStates:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='doublecircle')
        elif state.stateName == data.sinkState:
            pass
        elif state.stateName == data.errorState:
            dot.node(name=str(state.stateName), label=str(state.stateName), shape='box')
        else:
            dot.node(name=str(state.stateName), label=str(state.stateName))
    for tran in data.trans:
        if tran.source != data.sinkState and tran.target != data.sinkState:
            tranLabel = " " + str(tran.input) + " " + tran.showGuards() + " " + str(tran.isReset)
            dot.edge(str(tran.source), str(tran.target), tranLabel)
    newFilePath = filePath + fileName
    dot.render(newFilePath, view=True)
