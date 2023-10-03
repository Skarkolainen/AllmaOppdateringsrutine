#coding=utf-8

# Metoder for spesialtilfeller
import arcpy
import re

#gjTiltak = [{u'!Salesopp!': 0, u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 240, u'!AARSTALL!': 2020, u'!STATE!': 1, u'!OBJECTID!': 1558656, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{FA711739-7627-42D4-AB1B-7CDE8BF93F9F}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'},
#            {u'!Salesopp!': 0,u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 1, u'!AARSTALL!': 2023, u'!STATE!': 1, u'!OBJECTID!': 1558666, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{F6ABCDFB-562D-49A0-AE71-0EE6AD5D3C99}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'}
#            ]




def finnTreAntall(tiltaket):

    tekst = tiltaket[u'!KOMMENTAR!']
    if tekst is None:
        return False

    print tekst

    pattern = r'\b\d{3}\b'
    matches = re.findall(pattern, tekst)

    lastInt = int(matches[-1])

    if lastInt >= 70 and lastInt <= 300:
        return lastInt

    return False


    ### Gammel måte under, sjekker mot spesifikk benevning i tillegg til siffer..
    #tekst = unicode(tekst, "utf-8")
    #tekst = tekst.replace(" ", "")
    #tekst = tekst.lower()
    # tekst = tekst.replace("æ", "ae")

    #regex = re.compile(
    #    ur'(\d{2,4})(trærpr.dekar|trær/daa|trær/da|/daa|ant/daa|three/daa|trees/da|trees/daa|/dekar|traer/da|/da|ant/da|three/da|prda|prdaa|trærpr/daa|trærpr/da|stk/dekar|stk/daa|stk/da|pr.da|cutto)',
    #    re.I)
    #regex2 = re.compile(ur'(tetthet|tethet|tettet|after|aftercutting|aftercut|e.reg|etterreg)(\d{2,4})', re.I)
    #mo1 = regex.findall(tekst)
    #mo2 = regex2.findall(tekst)

    #treAntall = []

    #if len(mo1) == 1:
    #    treAntall.append(mo1[0][0])
    #if len(mo2) == 1:
    #    treAntall.append(mo2[0][1])
    #
    #if len(treAntall) == 1:
    #    treAntall=int(treAntall[0])
    #    if treAntall >= 70 and treAntall <= 300:
    #        return treAntall
    #else:
    #    return False


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
        "Frotrestilling": {
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
        "Forhandsrydding":{
            400,
            401,
            402,
            403
        },
        "Gjodsling": {
            610
        }
        ,
        "Suppleringsplanting": {
            200
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
    elif dict_internal["$RutineNavn$"][:20] == u'EDEL_utført_planting':
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


def settGjTiltak_2(settGjTiltak, rutinenavn, gjennomforteTiltak):
    if settGjTiltak:
        tiltaketFinnes = False
        if rutinenavn == 'EDEL_utført_flatehogst':
            tiltaketFinnes = tiltakFinnes('Flatehogst', gjennomforteTiltak)[0]
        elif rutinenavn[:20] == u'EDEL_utført_planting':
            tiltaketFinnes = tiltakFinnes('Planting', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_frøtrestilling':
            tiltaketFinnes = tiltakFinnes('Frotrestilling', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_tynning':
            tiltaketFinnes = tiltakFinnes('Tynning', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_ungskogpleie':
            tiltaketFinnes = tiltakFinnes('Ungskogpleie', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_gjødsling':
            tiltaketFinnes = tiltakFinnes('Gjodsling', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_forhåndsrydding_før_tynning':
            tiltaketFinnes = tiltakFinnes('Forhandsrydding', gjennomforteTiltak)[0]
        elif rutinenavn == 'EDEL_utført_suppleringsplanting':
            tiltaketFinnes = tiltakFinnes('Suppleringsplanting', gjennomforteTiltak)[0]

        return not tiltaketFinnes

    return False  # Tiltak skal ikke lages
