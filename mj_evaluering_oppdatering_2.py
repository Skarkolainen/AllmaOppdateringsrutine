#coding=utf-8
import re
import mj_evaluering_oppdatering as evaluering_oppdatering_1
import mj_oppdateringsrutine_metoder as metoder

def tabellOppslag(bestandet, dict_internal, oppslagskode, gjTiltaksliste, rutiner ):
    return evaluering_oppdatering_1.tabellOppslag(bestandet, dict_internal, oppslagskode, gjTiltaksliste, rutiner)

def replace_tableLookups(setning, dict_internal_verdier, dict_external_verdier, gj_Tiltak, tabeller):

    def lookup(match):
        #Hvis det er treantall etter ungskogpleie, sjekk om det er treantall i kommentarfeltet.

        tabellnavn = match.group(1)
        if tabellnavn == 'TreantallEtterUngskogpleie':

            tiltakFinnes = metoder.tiltakFinnes('Ungskogpleie', gj_Tiltak)
            # Forutsetter at gjennomført ungskogpleietiltak finnes.
            if tiltakFinnes[0]:
                treAntall =  metoder.finnTreAntall(tiltakFinnes[1])

                if treAntall: #Treantall ble funnet i kommentarfelt, dette benyttes
                    return str(treAntall)
                #Treantall ble ikke funnet i tiltaket, benytter treantall/daa hvis den er større enn null og mindre enn treantallFØR
                elif dict_external_verdier[u'!TREANT_DAA!'] > 0 and dict_external_verdier[u'!TREANT_DAA!'] < dict_external_verdier[u'!TREANT_DAA_FOER!']:
                    return str(dict_external_verdier[u'!TREANT_DAA!'])

            # Ikke funnet gjennomført tiltak, benytter treantall/daa hvis den er større enn null og mindre enn treantallFØR
            elif dict_external_verdier[u'!TREANT_DAA!'] > 0 and dict_external_verdier[u'!TREANT_DAA!'] < dict_external_verdier[u'!TREANT_DAA_FOER!']:
                return str(dict_external_verdier[u'!TREANT_DAA!'])

        elif tabellnavn == 'TreantallEtterForyngelse_Ikke_Markberedt' or tabellnavn == 'TreantallEtterForyngelse_Markberedt':

            tiltakFinnes = metoder.tiltakFinnes('Planting', gj_Tiltak)
            # Forutsetter at gjennomført ungskogpleietiltak finnes.
            if tiltakFinnes[0]:
                treAntall =  metoder.finnTreAntall(tiltakFinnes[1])

                if treAntall: #Treantall ble funnet i kommentarfelt, dette benyttes
                    return str(treAntall)


        #Treantall ble ikke funnet i tiltaket, fortsetter med tabelloppslag


        #finn riktig tabell
        for table in tabeller:
            if table['tabellnavn'] == tabellnavn:
                theTable = table


        # Hent oppslagskode fra tabellen

                oppslagskode = theTable['oppslagskode']
                oppslagskode = oppslagskode.replace(" ","")
                oppslagskode = oppslagskode.split(';')

                oppslagsverdier =[]

                for kode in oppslagskode:
                    if kode[0] == "!": oppslagsverdier.append(str(dict_external_verdier[kode]))
                    elif kode[0] == "$": oppslagsverdier.append(dict_internal_verdier[kode])


        # Slå opp
                for i in range (0, len(oppslagsverdier)):
                    try:
                        theTable = theTable[oppslagsverdier[i]]
                    except:
                        return None

                verdi = theTable
                break

        try:
            if verdi:
                return str(verdi)
        except:
            return None

    pattern = r'@(\w+)@'
    result = re.sub(pattern, lookup, setning)
    return result


def replace_variables_in_string(input_string, variable_dict, enclosingChar):

    #pattern = r'!(\w+)!'
    #pattern = re.compile(r'{0}(.*?){0}'.format(re.escape(enclosingChar)), re.UNICODE)

    pattern = r'{0}([^={0}\s]*){0}'.format(re.escape(enclosingChar))

    def replace_variable(match):
        # Extract the variable name from the match
        mat = match.group(1)
        variable_name = "{0}{1}{0}".format(enclosingChar, mat)
        empty = "{0}{0}".format(enclosingChar)

        if variable_name != empty and variable_name not in variable_dict:
            raise ValueError("Variable '{}' not found in the dictionary.".format(variable_name))
        res = variable_dict.get(variable_name, match.group(0))
        return unicode(res)
        #return variable_dict[variable_name]

    #  re.sub to replace all matched variables in the input string
    result_string = re.sub(pattern, replace_variable, input_string, flags=re.UNICODE )

    return result_string

def reArrangeTernaryExpression(input_string):
    ## "condition ? onTrue : onFalse" ->
    ## onTrue if condition else onFalse
    if input_string.count("?") > 1:
        raise NotImplementedError("Rearrangement of more than one ternary is not implemented. Rewrite expression to Python syntax.")
    try:
        oldTernary = input_string.strip()
        condition, rest = oldTernary.split('?')
        onTrue, onFalse = rest.split(':')

    except Exception as e:
        raise ValueError("Error in rearranging ternary({}) : {}".format(input_string, e))


    pythonTernary = "({}) if ({}) else ({})".format(onTrue, condition, onFalse)
    return pythonTernary

def toInt(value):
    try:
        return int(value)
    except:
        return 0

def Uttrykk(setning, dict_internal, dict_external, gj_tiltak, tabeller ):
    #print "uttrykk: {}".format(setning)
    #setning = unicode(setning, 'utf-8')

    # Contains external variable
    if setning.count("!") > 1:
        setning = replace_variables_in_string(setning, dict_external, "!")
        #print setning

    # Contains internal variable
    if setning.count("$") > 1:
        setning = replace_variables_in_string(setning, dict_internal, "$")
        #print setning

    #Contains tablelookup
    if setning.count("@")> 1:
        setning = replace_tableLookups(setning, dict_internal, dict_external, gj_tiltak, tabeller)

    # Contains ternary expression
    if setning.count("?") > 0 and setning.count(":") > 0:
        setning = reArrangeTernaryExpression(setning)

    setning = (setning.replace('&&',' and ')
               .replace('||', ' or ')
               .replace('None', '0') # En del verdier som det testes mot i bestandet er null/ None, men brukes forventer int..
               )

    #print setning

    result = None
    try:

        result = eval(setning)
    except SyntaxError:
        raise ValueError("\n Invalid expression syntax:\n {} \n".format(setning))
    #except Exception as e:
    #    raise ValueError("Error evaluating the expression({}) : {}".format(setning, e))
    #print("resultat: {}".format(result))
    return (True, result, setning )

def evaluerTre(value):
    return value


#gj_tiltak = ""
#tabeller = ""

#setninger = []
#setninger.append("!MARKSLAG!>0 && !MARKSLAG!<30 && !HOGSTKLASSE!>=3 && !BONTRESLAG! != 3")
#Erdetnoktraeriminsteklasse = "( !DIMU_15! - (!TREANT_DAA!*0.1))  if (!DIMU_15! - (!TREANT_DAA!*0.1)) > 0 else 0"

#setninger.append(Erdetnoktraeriminsteklasse)

#aarGml = "$NOW_MONTH$<7?$NOW_YEAR$:$NOW_YEAR$+1"
#setninger.append("$NOW_YEAR$ if $NOW_MONTH$<7 else $NOW_YEAR$+1")
#setninger.append("$NOW_MONTH$<2")
#setninger.append("($NOW_MONTH$<5 || 7<5) || 5>3")
#setninger.append("3>2&&2>3||3>2")
#setninger.append("!MARKSLAG!>0 && !MARKSLAG!<30 && !HOGSTKLASSE! ne 2 && !BONTRESLAG! ne 3")

#print eval("3>2&2>3||3>2")
#dict_internal = {"$NOW_YEAR$":2023,"$NOW_MONTH$":4}

#dict_external = {"!MARKSLAG!":20,"!HOGSTKLASSE!":4, "!BONTRESLAG!":3, "!DIMU_15!": 10, "!TREANT_DAA!": 100}


#for i in setninger:
#    print Uttrykk(i, dict_internal, dict_external, gj_tiltak, tabeller)

# print("eval:")
#print eval("20>0 & 20<30 & 4>=3 & 1 != 3")
#print not metoder.settGjTiltak_2(True,"EDEL_utfort_flatehogst", {})
#print eval("metoder.settGjTiltak_2(True,'EDEL_utfort_flatehogst', {})")

#val = uttrykk("!MARKSLAG!>0 && !MARKSLAG!<30 && !HOGSTKLASSE! ne 2 && !BONTRESLAG! ne 3", dict_internal, dict_external, gj_tiltak, tabeller)

#print evaluerTre(val)