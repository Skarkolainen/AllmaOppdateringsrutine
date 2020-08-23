

import json
import os
import copy

jsonFile = u"C:\\dev-python\\AllmaOppdateringsrutine\\mj_oppdateringsrutiner.json"

data = json.loads(open(jsonFile).read())

tables = data['tabeller']

tabelloppslagsKode = "TreantallEtterForyngelse;gran;6;hei"
tabelloppslagsKode = "Hogstklasser;bar;20;5"
tabellOppslag = tabelloppslagsKode.split(';')
mapList = tabellOppslag[1:]

tabellnavn = tabellOppslag[0]
theTable = None

for table in tables:
    if table['tabellnavn'] == tabellnavn:
        theTable = table


def getFromDict(dataDict, mapList):
    for k in mapList: dataDict = dataDict[k]
    return dataDict



value = getFromDict(theTable, mapList)

print(value)





