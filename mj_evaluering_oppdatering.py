import operator
import re
import json
import os
import copy

hogstaar = 2019
hogstmaaned = 3


test_dict_internal_verdier = {"$NOW_YEAR$":hogstaar,"$NOW_MONTH$":hogstmaaned}
test_dict_external_verdier = {"!MARKSLAG!":20,"!BONTRESLAG!":1}

op_precedence = ["(",")","*","/","+","-","<","<=",">",">=","<>","==","and","or"]
op_aritmetriske = ["+","-","*","/"]
op_logiske = ["==","<>",">=","<=",">","<"]
op_and_or = ["||","&&"]

ops = {"==":operator.eq,"!=":operator.ne,">":operator.gt,"<":operator.lt,">=":operator.ge,"<=":operator.le,"+":operator.add,"-":operator.sub,"*":operator.mul,"/":operator.div, "||":operator.or_,"&&":operator.and_}

def evaluer_funk(a,b,o):
    return o(a,b)

def fjern_paranteser(setning_med_mulige_paranteser):
    retur_setning = setning_med_mulige_paranteser
    if retur_setning != None:
        retur_setning = retur_setning.replace(" ","")
        if len(retur_setning)>2:
            if retur_setning[0]=="(" and retur_setning[-1]==")":
                retur_setning = retur_setning[1:-1]
                retur_setning = fjern_paranteser(retur_setning)
    return retur_setning

def tell_opp_paranteser(setning_med_mulige_paranteser, utgangspunkt):
    ant_venstre_foer = setning_med_mulige_paranteser[0:utgangspunkt].count("(")
    ant_hoyre_foer = setning_med_mulige_paranteser[0:utgangspunkt].count(")")
    ant_venstre_etter = setning_med_mulige_paranteser[utgangspunkt:].count("(")
    ant_hoyre_etter = setning_med_mulige_paranteser[utgangspunkt:].count(")")
    return (ant_venstre_foer-ant_hoyre_foer,ant_hoyre_etter-ant_venstre_etter)

def finn_mulig_tegn_i_streng(mulig_tegn,streng,startpos=0):
    try:
        ret_s = None
        lengde_streng = len(streng)
        for pos in range(lengde_streng):
            if pos>=startpos:
                #for t in mulig_tegn:
                t = mulig_tegn
                if (len(t)+pos)<lengde_streng:
                    if t == streng[pos:pos+len(t)]:
                        ret_s = (t, pos)
                        return ret_s
        return ret_s
    except:
        return None

def telling_cond_operatorer_fix(setning,op_cond):
    antall = 0
    for i in range(len(setning)-1):
        for o in op_cond:
            if o == setning[i:(i+(len(o)))]:
                antall+=1
                break
    return antall

def telling_log_operatorer(setning,op_log):
    antall = 0
    for i in range(len(setning)-1):
        for o in op_log:
            if o==setning[i:(i+(len(o)))]:
                antall+=1
                break
    return antall

def isLogical(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    antall_operatorer=0
    retursvar = None
    if len(setning_s)>2:
        antall_operatorer = telling_log_operatorer(setning_s,op_and_or)
        if antall_operatorer==1:
            for tegn in op_and_or:
                try:
                    svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s)
                    del1 = setning_s[svar_finn_tegn[1]:svar_finn_tegn[1]+len(svar_finn_tegn[0])]
                    del2 = setning_s[:svar_finn_tegn[1]]
                    del3 = setning_s[(svar_finn_tegn[1]+len(svar_finn_tegn[0])):]

                    return (del1,del2,del3)
                except:
                    retursvar = None
        elif antall_operatorer==0:
            return None
        elif antall_operatorer>1:
            splittepunkt = None
            minste_antall_paranteser = 9999
            storste_antall_paranteser = -9999

            #PLUS, MINUS, GANGE, DELE
            #Foerst finne om noen har farre paranteser
            operatorposisjoner=set()
            if len(setning_s)>0:

                for kpos in range(len(setning_s)):
                    for tt in op_and_or:
                        try:
                            if tt == setning_s[kpos:(kpos+len(tt))]:
                                operatorposisjoner.add(kpos)
                        except:
                            pass
            liste = list(operatorposisjoner)
            liste = sorted(liste)
            for op_pos in liste:

                for tegn in op_and_or:
                    try:
                        svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s,op_pos)
                        pos = svar_finn_tegn[1]
                        ant_par = tell_opp_paranteser(setning_s,pos)
                        if ant_par[0]<minste_antall_paranteser:
                            splittepunkt=svar_finn_tegn
                            minste_antall_paranteser=ant_par[0]
                        if ant_par[0]>storste_antall_paranteser:
                            storste_antall_paranteser=ant_par[0]
                    except:
                        pos = None
            for tegn in op_and_or:
                for op_pos in liste:
                    try:
                        svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s,op_pos)
                        pos = svar_finn_tegn[1]
                        ant_par = tell_opp_paranteser(setning_s,pos)
                        if ant_par[0]==minste_antall_paranteser:
                            del1 = setning_s[svar_finn_tegn[1]:svar_finn_tegn[1]+len(svar_finn_tegn[0])]
                            del2 = setning_s[:svar_finn_tegn[1]]
                            del3 = setning_s[(svar_finn_tegn[1]+len(svar_finn_tegn[0])):]
                            return (del1,del2,del3)
                    except:
                        pos=None
            else:
                return None
        else:
            return None
    else:
            return None



def isConditional(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    antall_operatorer=0
    retursvar = None
    if len(setning_s)>2:
        antall_operatorer = telling_cond_operatorer_fix(setning_s,op_logiske)
        #for tegn in op_logiske:
            #antall_operatorer += setning_s.count(tegn)

        if antall_operatorer==1:
            for tegn in op_logiske:
                try:
                    svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s)
                    del1 = setning_s[svar_finn_tegn[1]:svar_finn_tegn[1]+len(svar_finn_tegn[0])]
                    del2 = setning_s[:svar_finn_tegn[1]]
                    del3 = setning_s[(svar_finn_tegn[1]+len(svar_finn_tegn[0])):]

                    return (del1,del2,del3)
                except:
                    retursvar = None
        elif antall_operatorer==0:
            return None
        else:
            return None

def isAritmetrisk(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    #Paranteser
    antall_operatorer=0
    retursvar = None
    if len(setning_s)>2:
        streng_posisjoner=set()
        for tegn in op_aritmetriske:
            antall_operatorer += setning_s.count(tegn)
        if antall_operatorer==1:
            for tegn in op_aritmetriske:
                try:
                    svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s)
                    del1 = setning_s[svar_finn_tegn[1]:svar_finn_tegn[1]+len(svar_finn_tegn[0])]
                    del2 = setning_s[:svar_finn_tegn[1]]
                    del3 = setning_s[(svar_finn_tegn[1]+len(svar_finn_tegn[0])):]

                    return (del1,del2,del3)
                except:
                    retursvar = None
        elif antall_operatorer==0:
            return None
        elif antall_operatorer>1:
            splittepunkt = None
            minste_antall_paranteser = 9999
            storste_antall_paranteser = -9999

            #PLUS, MINUS, GANGE, DELE
            #Foerst finne om noen har farre paranteser
            operatorposisjoner=set()
            if len(setning_s)>0:

                for kpos in range(len(setning_s)):
                    for tt in op_aritmetriske:
                        if tt == setning_s[kpos]:
                            operatorposisjoner.add(kpos)
            liste = list(operatorposisjoner)
            liste = sorted(liste)
            for op_pos in liste:

                for tegn in op_aritmetriske:
                    try:
                        svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s,op_pos)
                        pos = svar_finn_tegn[1]
                        ant_par = tell_opp_paranteser(setning_s,pos)
                        if ant_par[0]<minste_antall_paranteser:
                            splittepunkt=svar_finn_tegn
                            minste_antall_paranteser=ant_par[0]
                        if ant_par[0]>storste_antall_paranteser:
                            storste_antall_paranteser=ant_par[0]
                    except:
                        pos = None
            for tegn in op_aritmetriske:
                for op_pos in liste:
                    try:
                        svar_finn_tegn = finn_mulig_tegn_i_streng(tegn,setning_s,op_pos)
                        pos = svar_finn_tegn[1]
                        ant_par = tell_opp_paranteser(setning_s,pos)
                        if ant_par[0]==minste_antall_paranteser:
                            del1 = setning_s[svar_finn_tegn[1]:svar_finn_tegn[1]+len(svar_finn_tegn[0])]
                            del2 = setning_s[:svar_finn_tegn[1]]
                            del3 = setning_s[(svar_finn_tegn[1]+len(svar_finn_tegn[0])):]
                            return (del1,del2,del3)
                    except:
                        pos=None
            else:
                return None
        else:
            return None
    else:
        return None


def isOperand(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    if len(setning_s)<=2 and len(setning_s)>=1:
        if ops.has_key(setning_s):
            return ops[setning_s]
        else:
            return None
    else:
        return None


def isIfElse(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    try:
        pos1 = finn_mulig_tegn_i_streng("?",setning_s)
        pos2 = finn_mulig_tegn_i_streng(":",setning_s)
        del1 = setning_s[0:pos1[1]]
        del2 = setning_s[(int(pos1[1])+1):pos2[1]]
        del3 = setning_s[(int(pos2[1])+1):]
        if del1.count("(")>0:
            return None
        else:
            return (del1,del2,del3)
    except:
        return None

def isNumber(setning):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    try:
        if "." in setning_s:
            return float(setning_s)
        else:
            return int(setning_s)

    except ValueError:
        return None

def isInternalVariable(setning,dict_internal_verdier):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    if setning_s[0]=="$" and setning_s[-1]=="$":
        try:
            if dict_internal_verdier.has_key(setning_s):
                return dict_internal_verdier[setning_s]
        except:
            return None
    else:
        return None

def isExternalVariable(setning,dict_external_verdier):
    setning_s = setning.replace(" ","")
    setning_s = fjern_paranteser(setning_s)
    if setning_s[0]=="!" and setning_s[-1]=="!":
        try:
            if dict_external_verdier.has_key(setning_s):
                return dict_external_verdier[setning_s]
        except:
            return None
    else:
        return None


def evaluer_hviselse(a,b,o):
    if o==True:
        return a
    elif o==False:
        return b
    else:
        return None

def gaa_gjannom(tt):
    a = isIfElse(tt)
    if isinstance(a,tuple):
        #tt = a
        tt = list()
        tt.append(gaa_gjannom(a[1]))
        tt.append(gaa_gjannom(a[2]))
    else:
        tt=tt
    return tt

class Uttrykk:
    def __init__(self,tekststreng,dict_internal_verdier,dict_external_verdier,parent=None):
        self.tekststreng = tekststreng
        self.svar = None
        self.fsvar = None
        self.beregnet = None
        self.parent = None   #annet Uttrykk
        self.left = None     #text / annet Uttrykk
        self.left_type = None
        self.right = None    #text / annet Uttrykk
        self.right_type = None
        self.optor = None   # text / annet Utrykk
        self.optor_type = None
        #conditional
        #aritmetrisk
        #tall
        #operator
        #internverdi
        #externverdi
        kontr_ifelse = isIfElse(self.tekststreng)
        if isinstance(kontr_ifelse,tuple):
            self.optor_type = "ifelse"
            self.optor = Uttrykk(kontr_ifelse[0],dict_internal_verdier,dict_external_verdier,self)
            self.left_type = "str_eq"
            self.left = Uttrykk(kontr_ifelse[1],dict_internal_verdier,dict_external_verdier,self)
            self.right_type = "str_eq"
            self.right = Uttrykk(kontr_ifelse[2],dict_internal_verdier,dict_external_verdier,self)
            self.beregnet=False
        else:
            kontr_arit = isAritmetrisk(self.tekststreng)
            if kontr_arit!=None:
                self.optor_type="Arit_"+kontr_arit[0]
                self.optor = Uttrykk(kontr_arit[0],dict_internal_verdier,dict_external_verdier,self)
                self.left_type = "str_eq"
                self.left = Uttrykk(kontr_arit[1],dict_internal_verdier,dict_external_verdier,self)
                self.right_type = "str_eq"
                self.right = Uttrykk(kontr_arit[2],dict_internal_verdier,dict_external_verdier,self)
                self.beregnet=False
            else:
                kontr_andor = isLogical(self.tekststreng)
                if kontr_andor!=None:
                    self.optor_type = "and_or"
                    self.optor = Uttrykk(kontr_andor[0],dict_internal_verdier,dict_external_verdier,self)
                    self.left_type = "and_or"
                    self.left = Uttrykk(kontr_andor[1],dict_internal_verdier,dict_external_verdier,self)
                    self.right_type = "and_or"
                    self.right = Uttrykk(kontr_andor[2],dict_internal_verdier,dict_external_verdier,self)
                    self.beregnet=False
                else:
                    kontr_cond = isConditional(self.tekststreng)
                    if isinstance(kontr_cond,tuple):
                        self.optor_type = "cond"
                        self.optor = Uttrykk(kontr_cond[0],dict_internal_verdier,dict_external_verdier,self)
                        self.left_type = "str_eq"
                        self.left = Uttrykk(kontr_cond[1],dict_internal_verdier,dict_external_verdier,self)
                        self.right_type = "str_eq"
                        self.right = Uttrykk(kontr_cond[2],dict_internal_verdier,dict_external_verdier,self)
                        self.beregnet=False
                    else:
                        kontr_tall = isNumber(self.tekststreng)
                        if kontr_tall!=None:
                            self.svar = kontr_tall
                            self.beregnet=True

                        else:
                            kontr_intern = isInternalVariable(self.tekststreng,dict_internal_verdier)
                            if kontr_intern != None:
                                self.svar = kontr_intern
                                self.beregnet=True
                            else:
                                kontr_extern = isExternalVariable(self.tekststreng,dict_external_verdier)
                                if kontr_extern != None:
                                  self.svar = kontr_extern
                                  self.beregnet=True

                                else:
                                    kontr_operand = isOperand(self.tekststreng)
                                    if kontr_operand !=None:
                                        self.svar = kontr_operand
                                        self.beregnet = True

                #sjekk om det er st?rre eller mindre enn etc.
                #sjekk om det er et tall
                #sjekk om det er en variabel

##
##    ferdig = False
##
##    def parse(self):
##        t_1 = isIfElse(self.tekststreng)
##        if isinstance(t_1,tuple):
##            s=Uttrykk(self.tekststreng)
##            s.optor = t_1[0]
##            s.left = t_1[1]
##            s.right = t_1[2]
##            s.parse()
##

def evaluerTre(root):
    if root:
        evaluerTre(root.optor)
        evaluerTre(root.right)
        evaluerTre(root.left)
        try:
            if (root.optor.beregnet==True and root.right.beregnet==True and root.left.beregnet==True):
                if root.optor_type=="ifelse":
                    ok=0
                    root.svar = evaluer_hviselse(root.left.svar,root.right.svar,root.optor.svar)
                    #print "VALG"
                    #print root.svar
                    if root.svar != None:
                        root.beregnet = True
                else:
                    ok=0
                    root.svar=evaluer_funk(root.left.svar,root.right.svar,root.optor.svar)
                    #print "BEREGNING"
                    #print root.svar
                    if root.svar != None:
                        root.beregnet = True
        except:
            pass

        #print (str(root.beregnet) + " " + str(root.svar) + " " + str(root.tekststreng))
        #return (str(root.beregnet) + " " + str(root.svar) + " " + str(root.tekststreng))
        return (root.beregnet,root.svar,root.tekststreng)

def tabellOppslag(bestandet, oppslagskode, rutine ):

    #jsonFile = u"C:\\Utvikling\\dev-python\\AllmaOppdateringsrutine\\mj_oppdateringsrutiner.json"
    jsonFile = rutine
    data = json.loads(open(jsonFile).read())
    tables = data['tabeller']

    tabellOppslagskode = oppslagskode.split(';')
    tabellnavn = tabellOppslagskode[0]
    theTable = None

    #Finn riktig tabell
    for table in tables:
        if table['tabellnavn'] == tabellnavn:
            theTable = table

    bestandsEgenskaper = copy.deepcopy(bestandet)

    for key,val in bestandsEgenskaper.items():
        if key == '!MERK!':
            # hopp over merknad, oppstår problem med æøå
            continue

        bestandsEgenskaper[key] = '{}'.format(bestandsEgenskaper[key])

    #Henter verdi fra dict basert på oppslagskoden.
    def getFromDict(dataDict, mapList):
        for k in mapList: dataDict = dataDict[bestandsEgenskaper[k]]
        return dataDict

    mapList = tabellOppslagskode[1:]
    value = getFromDict(theTable, mapList)

    return value


setningasdf = "((28+45)*15)"
setningasdf = "5967-(892*39)+(50*80)"
setningasdf = "580>=(5967-(892*39)+(50*80))?2:5>8*5?1:11"

#print setningasdf
#print str(isAritmetrisk(setningasdf))

#print str(tell_opp_paranteser(setningasdf,4))
#print str(tell_opp_paranteser(setningasdf,13))
#print str(tell_opp_paranteser(setningasdf,17))

setning2 = "$NOW_MONTH$<7?$NOW_YEAR$:$NOW_YEAR$+1"
setning2t = "5<7?2001:2001+1"
setning3 = "($NOW_MONTH$<2?$NOW_YEAR$:$NOW_YEAR$+1)+10"
setning4 = "$NOW_MONTH$<2"
setning5 = "($NOW_MONTH$<5 || 7<5) || 5>3"
setning5 = "3>2&&2>3||3>2"

aaa = Uttrykk(setning5,test_dict_internal_verdier,test_dict_external_verdier)
#aaa.parse()




print evaluerTre(aaa)

print 3>2 and 2>3 or 3>2