import configparser

def bracket(loc,sec,key):
    # add bracket [] when ( + or . if present for re
    config = configparser.RawConfigParser()
    config.read(loc)
    temp = []
    # store dict info to parse into list
    temp_list = dict(config.items(sec))[key]
    for i in temp_list.split(','):
        value = ""
        flag = 0
        for j in i:
            if j in ['(',')','+','-','.']:
                value = value+"["+j+"]"
                flag = 0
            elif j == " " and flag == 0:
                value = value+".*"
                flag = 1
            else:
                value = value+j
                flag = 0
        temp.append(value)
    config.set(sec, key+"1", ",".join(temp))
    with open(loc, 'w') as configfile:
        config.write(configfile)
    print(temp)


bracket("Config/config2019.cfg", "ITR_7", "last")

