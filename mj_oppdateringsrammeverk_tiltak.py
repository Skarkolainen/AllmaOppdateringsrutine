
# Start på omskriving til metode hvor tiltak er valgt, og ikke bestand. Skal velge rutine basert på tiltakstypen.

import json
import arcpy
import os
import mj_evaluering_oppdatering as evaluering_oppdatering
import mj_oppdateringsrutine_metoder
import mj_oppdateringsrammeverk as rverk
import copy




runAsTool = True

if runAsTool:
    filnavn_konfig = arcpy.GetParameterAsText(0)
    navn_rutine = arcpy.GetParameterAsText(1)
    hogstaar = int(arcpy.GetParameterAsText(2))
    hogstmaaned = int(arcpy.GetParameterAsText(3))
    gdb = arcpy.GetParameterAsText(4)
    slettTiltak = arcpy.GetParameter(5)
    settGjTiltak = arcpy.GetParameter(6)
    ForutsettTiltakGeometri = arcpy.GetParameter(7) # Hvis sann, forutsetter at bestandet har et gjennomført tiltak som matcher valgt rutine, med identisk geometri
    folder = arcpy.GetParameterAsText(8) #Skriver loggfil hvis feltet er fylt inn med gyldig sti


    flyttFremTiltak = False # Benyttes kun i gjødslingsrutina, setter True hvis den er valgt.
    flyttTiltakAar = 10 # Benyttes kun i gjødslingsrutina

    dict_internal = {"$NOW_YEAR$": hogstaar, "$NOW_MONTH$": hogstmaaned, "$RutineNavn$": navn_rutine,
                     "$SettGjTiltak$": settGjTiltak}

bestandLYR = 'BESTAND'
tiltakLYR = 'TILTAK'
eiendomLYR = 'EIENDOM'

desc = arcpy.Describe(tiltakLYR)
path = desc.path

arcpy.env.workspace=gdb

ant_seleksjon = rverk.GetSelectionCount(bestandLYR)
if ant_seleksjon != None:

    # Åpne og les inn rutiner og tabeller
    #Iterer tiltak:

    arcpy.AddMessage("\n Starter gjennomgang")

    edit = arcpy.da.Editor(gdb)
    edit.startEditing(False, True)
    edit.startOperation()

    with arcpy.da.UpdateCursor(tiltakLYR, ('OID@', 'SHAPE@', '*')) as cur_tiltak:
    # cur_bestand = arcpy.UpdateCursor(bestandLYR,fields=('OID@','SHAPE@','*'))
        for best_row in cur_tiltak:
            geo = best_row[1]
            oid_verdi = best_row[0]
            # Sjekk om det er rutine for tiltaket;hvis ja sjekk om bestandet geometri er lik bestandet, ellers hopp over.

            # Hent bestandet, send bestandsegenskaper til dict_external

            dict_external = rverk.hentVerdierBestand(bestandLYR, oid_verdi)

            rverk.pr("########\n bestands OID: " + str(oid_verdi))

	# Geometri lik bestandet, kjør vanlig oppdatering, sjekk av grunnleggende forutsetninger.
	# Årstall hentes fra tiltaket.
	# Når bestandet er igjennom, slett taksatornavn i tiltaket.
	# Skriv loggfil.
	# Så til neste tiltak.

