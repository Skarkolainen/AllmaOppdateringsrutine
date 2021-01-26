#coding=utf-8

# Metoder for spesialtilfeller
import arcpy
import os
import re
import codecs
import datetime

#gjTiltak = [{u'!Salesopp!': 0, u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 240, u'!AARSTALL!': 2020, u'!STATE!': 1, u'!OBJECTID!': 1558656, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{FA711739-7627-42D4-AB1B-7CDE8BF93F9F}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'},
#            {u'!Salesopp!': 0,u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 1, u'!AARSTALL!': 2023, u'!STATE!': 1, u'!OBJECTID!': 1558666, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{F6ABCDFB-562D-49A0-AE71-0EE6AD5D3C99}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'}
#            ]

def finnTreAntall(tiltaket):

    tekst = tiltaket[u'!KOMMENTAR!']
    if tekst is None:
        return False

    print tekst
    #tekst = unicode(tekst, "utf-8")
    tekst = tekst.replace(" ", "")
    tekst = tekst.lower()
    # tekst = tekst.replace("æ", "ae")

    regex = re.compile(
        ur'(\d{2,4})(trærpr.dekar|trær/daa|trær/da|/daa|ant/daa|three/daa|trees/da|trees/daa|/dekar|traer/da|/da|ant/da|three/da|prda|prdaa|trærpr/daa|trærpr/da|stk/dekar|stk/daa|stk/da|pr.da|cutto)',
        re.I)
    regex2 = re.compile(ur'(tetthet|tethet|tettet|after|aftercutting|aftercut|e.reg|etterreg)(\d{2,4})', re.I)
    mo1 = regex.findall(tekst)
    mo2 = regex2.findall(tekst)

    treAntall = []

    if len(mo1) == 1:
        treAntall.append(mo1[0][0])
    if len(mo2) == 1:
        treAntall.append(mo2[0][1])

    if len(treAntall) == 1:
        treAntall=int(treAntall[0])
        if treAntall >= 70 and treAntall <= 300:
            return treAntall
    else:
        return False


def tiltakFinnes(kategori, gjennomforteTiltak ):
    tiltakFinnes = False # tiltak skal lages
    dictKategori = {
        "Flatehogst": {
            500
        },
        "Planting": {
            150,
            156,
            157,
            597
        },
        u"Frøtrestilling": {
            520
        },
        "Tynning": {
            265,
            401,
            410,
            430,
            440,
            530
        },
        "Ungskogpleie": {
            240,
            250,
            260,
            265,
            401
        },
        "Gjodsling": {
            610
        }
    }
    tiltakstyper = dictKategori[kategori]

    tiltaket = None
    for type in tiltakstyper:
        for tiltak in gjennomforteTiltak:
            if tiltak['!TYPE!'] == type:
                tiltaket = tiltak
                tiltakFinnes = True

    return (tiltakFinnes, tiltaket)


def settGjTiltak(dict_internal, gjennomforteTiltak):
    if dict_internal["$RutineNavn$"] == u'EDEL_utført_flatehogst':
        return tiltakFinnes('Flatehogst', gjennomforteTiltak)[0]
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_planting/_flatehogst_og_planting':
        return tiltakFinnes('Planting', gjennomforteTiltak)[0]
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_frøtrestilling':
        return tiltakFinnes(u'Frøtrestilling', gjennomforteTiltak)[0]
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_tynning':
        return tiltakFinnes('Tynning', gjennomforteTiltak)[0]
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_ungskogpleie_forTESTING':
        return tiltakFinnes('Ungskogpleie',gjennomforteTiltak)[0]
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_gjødsling_forTESTING':
        return tiltakFinnes('Gjodsling',gjennomforteTiltak)[0]
    else:
        return True # Tiltak skal ikke lages


def metode(metodeNavn,dict_internal,dict_external_write, gjennomforteTiltak, tabeller) : #omskriv så denne kan fjernes
    if metodeNavn == 'settGjTiltak':
        if dict_internal['$SettGjTiltak$'] is True:
            lagTiltak = not settGjTiltak(dict_internal, gjennomforteTiltak)
            return lagTiltak

        else: return False

    else: return False


def logger(hovednr, bestandsnr, teignr, teignavn, fornavn, etternavn, epost, tiltak, folder):
    variable = vars()
    for k, v in variable.iteritems():
        if isinstance(v, unicode):
            v = unicode.strip(v)

        if v == '' or v == None:
            variable[k] = '<' + k.upper() + '>'
            #pr(variable[k])


    # Formuler setning

    setning = ''
    if variable['bestandsnr'] == '<BESTANDSNR>':
        setning = u'{0};{1} {2};{3};Gjennomført {4} er ajourført på din eiendom på teig {6}'
    else:
        setning = u'{0};{1} {2};{3};Gjennomført {4} er ajourført på din eiendom i bestand nr {5} på teig {6}'

    if variable['teignavn'] != '<TEIGNAVN>':
        #pr("teignavn ulik <TEIGNAVN>")
        #pr("teignavn: " + variable['teignavn'])
        setning = setning + u' ({7})'

    setning = setning.format(variable['hovednr'], variable['fornavn'], variable['etternavn'], variable['epost'],
                             variable['tiltak'], variable['bestandsnr'], variable['teignr'], unicode.upper(unicode(variable['teignavn'])))

    setning = setning + '\n'
    #pr( setning)
    # Opprett fil og skriv logg.
    nu = datetime.datetime.now()
    filnavn = u"AllmaAjourfLogg_" + nu.strftime('%d-%m-%y') + '.txt'

    filsti = os.path.join(folder,filnavn)

    nyFil = os.path.exists(filsti)




    file = codecs.open(filsti,'a', encoding='utf-8')

    if not nyFil:
        file.write(u'Første linje\n')

    file.write(setning)
    file.close()

