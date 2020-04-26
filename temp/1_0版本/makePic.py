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