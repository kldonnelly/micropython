
LOGLEVEL = 1


def SetLoglevel(loglevel: int):
    global LOGLEVEL
    LOGLEVEL = loglevel


def Log(*messages):
    global LOGLEVEL
    if type(messages[0]) is int:
        if messages[0] < LOGLEVEL:
            print(messages)
    else:
        print(messages)



