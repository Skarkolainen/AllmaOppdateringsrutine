#coding=utf-8

import arcpy


#gjTiltak = [{u'!Salesopp!': 0, u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 240, u'!AARSTALL!': 2020, u'!STATE!': 1, u'!OBJECTID!': 1558656, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{FA711739-7627-42D4-AB1B-7CDE8BF93F9F}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'},
#            {u'!Salesopp!': 0,u'!BESTAND_ID!': None, u'!SHAPE_Length!': 70.84597363054542, u'!ORDER_ID!': None, u'!AREALANDEL!': 0, u'!TYPE!': 1, u'!AARSTALL!': 2023, u'!STATE!': 1, u'!OBJECTID!': 1558666, u'!TILTAK_ID!': None, u'!PRIORITET!': 1, u'!KOMMENTAR!': None, u'!EIENDOM_ID!': 1091327, u'!SHAPE!': (307955.8510161943, 6573523.4723439645), u'!STATUS!': 2, u'!TAKSATOR_2!': None, u'!REG_AV!': u'SSK', u'!SHAPE_Area!': 322.62535189278424, u'!GlobalID!': u'{F6ABCDFB-562D-49A0-AE71-0EE6AD5D3C99}', u'!HOVEDNR!': None, u'!ENDRET_AV!': u'SSK'}
#            ]


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
        }
    }
    tiltakstyper = dictKategori[kategori]

    for type in tiltakstyper:
        for tiltak in gjennomforteTiltak:
            if tiltak['!TYPE!'] == type:
                tiltakFinnes = True


    return tiltakFinnes



def settGjTiltak(dict_internal, gjennomforteTiltak):
    if dict_internal["$RutineNavn$"] == u'EDEL_utført_flatehogst':
        return tiltakFinnes('Flatehogst', gjennomforteTiltak)
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_planting/_flatehogst_og_planting':
        return tiltakFinnes('Planting', gjennomforteTiltak)
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_frøtrestilling':
        return tiltakFinnes(u'Frøtrestilling', gjennomforteTiltak)
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_tynning':
        return tiltakFinnes('Tynning', gjennomforteTiltak)
    elif dict_internal["$RutineNavn$"] == u'EDEL_utført_ungskogpleie_forTESTING':
        return tiltakFinnes('Ungskogpleie',gjennomforteTiltak)
    else:
        return True # Tiltak skal ikke lages



def metode(metodeNavn,dict_internal,dict_external_write, gjennomforteTiltak, tabeller) :
    if metodeNavn == 'settGjTiltak':
        if dict_internal['$SettGjTiltak$'] is True:
            lagTiltak = not settGjTiltak(dict_internal, gjennomforteTiltak)
            return lagTiltak

        else: return False

    else: return False


