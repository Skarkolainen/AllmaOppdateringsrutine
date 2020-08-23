import json
import os
import copy

jsonFile = u"C:\\dev-python\\AllmaOppdateringsrutine\\mj_oppdateringsrutiner.json"
data = json.loads(open(jsonFile).read())
tables = data['tabeller']

dict_external = {u'!MARKSLAG!': u'17', u'!BONTRESLAG!': u'2', u'!HOGSTKLASSE!': u'4'}
tabelloppslagsKode = "TreantallEtterForyngelse;!BONTRESLAG!;!MARKSLAG!"
tabelloppslagsKode = "Hogstklasser;!BONTRESLAG!;!MARKSLAG!;!HOGSTKLASSE!"

def getFromDict(dataDict, mapList):
    for k in mapList: dataDict = dataDict[dict_external[k]]
    return dataDict

tabellOppslag = tabelloppslagsKode.split(';')
tabellnavn = tabellOppslag[0]


theTable = None
for table in tables:
    if table['tabellnavn'] == tabellnavn:
        theTable = table


mapList = tabellOppslag[1:]

value = getFromDict(theTable, mapList)

print(value)
