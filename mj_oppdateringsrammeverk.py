#Rammeverk for ajourholdingsverktøy
#Vegard Lien, Glommen Mjøsen Skog 2019/2020


import json
import arcpy
import os
import mj_evaluering_oppdatering as evaluering_oppdatering
import copy

runAsTool = True

if runAsTool:
    filnavn_konfig = arcpy.GetParameterAsText(0)
    navn_rutine = arcpy.GetParameterAsText(1)
    hogstaar = int(arcpy.GetParameterAsText(2))
    hogstmaaned = int(arcpy.GetParameterAsText(3))
    gdb = arcpy.GetParameterAsText(4)
    slettTiltak = arcpy.GetParameter(5)

else:
    filnavn_konfig = u'c:\\AllmaToolbox\\Scripts\\oppdateringsrutiner.json'
    navn_rutine = u'EDEL_sluttavvirkning'
    hogstaar = 2020
    hogstmaaned = 3

    gdb = u'C:\\allma_effekt\\utsjekk_eidskog_13sept2019.gdb'
    #gdb = u'C:\\allma_effekt\\a.gdb'
    arcpy.env.workspace = gdb

    tiltak_fc = os.path.join(gdb,u'Topologi_valideres',u'TILTAK')
    bestand_fc = os.path.join(gdb,u'Topologi_valideres',u'BESTAND')

#BESTAND_IDer = [909968181,909968209,909968139]

def hentVerdierBestand(fcBestand,objectid):
    retur_dictionary = {}
    feltnavn_id = {}
    verdier = []
    oid_query = 'OBJECTID = ' +str(objectid)
    rec_teller=0
    with arcpy.da.SearchCursor(fcBestand,'*',where_clause=oid_query) as cur_best1:
        fields = cur_best1.fields
        for r in cur_best1:
            rec_teller += 1
            for field in fields:
                retur_dictionary["!" + field +"!"] = r[cur_best1.fields.index(field)]
    if rec_teller==1:
        return retur_dictionary
    else:
        return None

def finnRutinenummer(filnavn,rutinenavn):
    rutineteller=None
    rutineteller_valid = False
    with open(filnavn) as json_file:
        data = json.load(json_file)
        rutiner = data[u'oppdateringsrutiner']
        rutineteller = 0
        for rr in rutiner:
            if rr.has_key(u'rutinenavn'):
                rutineteller_valid=True
                if rr[u'rutinenavn'] == navn_rutine:
                    valg_rutinenummer = rutineteller
                rutineteller+=1
    if rutineteller_valid:
        pr(valg_rutinenummer)
        pr(navn_rutine)
        return valg_rutinenummer
    else:
        return None

def pr(text):
    arcpy.AddMessage(unicode(text))
    print unicode(text)


def GetSelectionCount(layer):
    try:
        desc = arcpy.Describe(layer)
        ff = desc.FIDSet

        if len(ff)>0:
            antall = int(arcpy.GetCount_management(layer).getOutput(0))
            return antall
        else:
            return None
    except:
        return None


#layer_tiltak = arcpy.MakeFeatureLayer_management(tiltak_fc,lyr_tiltak)

def lag_tiltak(fc_tiltak_ut,t_type,t_prio,t_status,t_aar,t_kommentar,t_arealandel,polygonet,hovednummer=None,bestandid=None,eiendomid=None):
    #desc_geo = arcpy.Describe(polygonet)
    sp = polygonet.spatialReference
    #print sp.name
    #fc_layer = layer_tiltak.dataSource()
    #edits = arcpy.da.Editor(gdb)
    #was_editing = edits.isEditing
    #if not was_editing:
    #edits.startEditing(False,False)
    #edits.startOperation()
    felter_tiltak = ['TYPE','PRIORITET','AARSTALL','STATUS','KOMMENTAR','AREALANDEL','TILTAK_ID','ORDER_ID','STATE','SHAPE@','HOVEDNR','BESTAND_ID','EIENDOM_ID']
    #print tiltak_fc
    with arcpy.da.InsertCursor(fc_tiltak_ut,felter_tiltak) as ins_tiltak_cur:
        inn_rad = tuple([t_type,t_prio,t_aar,t_status,t_kommentar,t_arealandel,None,None,1,polygonet,hovednummer,bestandid,eiendomid])
        ins_tiltak_cur.insertRow(inn_rad)
    #edits.stopOperation()
    #
    #if not was_editing:
    #edits.stopEditing(True)
    #del ins_tiltak_cur
    return True






dict_internal = {"$NOW_YEAR$":hogstaar,"$NOW_MONTH$":hogstmaaned}

bestandLYR = 'BESTAND'
tiltakLYR = 'TILTAK'

desc = arcpy.Describe(bestandLYR)
path = desc.path
#arcpy.env.workspace=u'Database Connections\\test@PlanTestFelles-AllmaplanNY.sde'
#arcpy.AddMessage(path)
arcpy.env.workspace=gdb


if runAsTool==False:
    arcpy.MakeFeatureLayer_management(bestand_fc,bestandLYR)
    arcpy.MakeFeatureLayer_management(tiltak_fc,tiltakLYR)

if runAsTool==False:
    arcpy.SelectLayerByAttribute_management(bestandLYR,"NEW_SELECTION","BESTAND_ID IN (909968181,909968209,909968139)")

ant_seleksjon = GetSelectionCount(bestandLYR)
if ant_seleksjon != None:
    aa = 1

    #cur_bestand = arcpy.da.SearchCursor(bestand_fc,('BESTAND_ID','MARKSLAG','BONTRESLAG','OID@','SHAPE@'),where_clause="BESTAND_ID IN "+str(tuple(BESTAND_IDer)))

    valg_rutinenummer = finnRutinenummer(filnavn_konfig,navn_rutine)
    if valg_rutinenummer != None:
        with open(filnavn_konfig) as json_file:
            data = json.load(json_file)
            rutiner = data[u'oppdateringsrutiner']
            valgt_rutine = rutiner[valg_rutinenummer]
            #arcpy.AddMessage(rutiner[valg_rutinenummer])
            arcpy.AddMessage("\n Starter gjennomgang")

            edit = arcpy.da.Editor(gdb)
            edit.startEditing(False, True)
            edit.startOperation()
            cur_bestand = arcpy.da.UpdateCursor(bestandLYR,('OID@','SHAPE@','*'))
            #cur_bestand = arcpy.UpdateCursor(bestandLYR,fields=('OID@','SHAPE@','*'))
            for best_row in cur_bestand:
                geo = best_row[1]
                oid_verdi = best_row[0]
                dict_external = hentVerdierBestand(bestandLYR,oid_verdi)
    ##    dict_external[u'!MARKSLAG!']=best_row[1]
    ##    dict_external[u'!BONTRESLAG!']=best_row[2]
    ##    dict_external[u'!HOGSTKLASSE!']=5           ####EKSEPM
    ##    dict_external[u'!BER_VOLUDAA!']=5
    ##    dict_external[u'!BER_VOLUMTOT!']=5
    ##    dict_external[u'!ALDER!']=5

                # arcpy.Delete_management(os.path.join("in_memory", "Temp_TILTAK"))


                #Kontroller om rutinen kan brukes:
                init_forutsetninger_sjekk = False
                if valgt_rutine.has_key(u'forutsetninger'):
                    init_forutsetninger=False
                    init_forutsetninger = valgt_rutine[u'forutsetninger']
                    uttrykk_forutsetninger = evaluering_oppdatering.Uttrykk(init_forutsetninger,dict_internal,dict_external)
                    uttrykk_forutsetninger_eval = evaluering_oppdatering.evaluerTre(uttrykk_forutsetninger)
                    if uttrykk_forutsetninger_eval!=None:
                        if uttrykk_forutsetninger_eval[0]:
                            if uttrykk_forutsetninger_eval[1]:
                                init_forutsetninger_sjekk = True
                                pr("Bestandet innfrir folgende grunnleggende betingelser: " + uttrykk_forutsetninger_eval[2])
                            else:
                                init_forutsetninger_sjekk = False
                                pr("Bestandet innfrir IKKE folgende grunnleggende betingelser: " + uttrykk_forutsetninger_eval[2])

                else:
                    init_forutsetninger_sjekk = True
                    pr(u"Ingen grunnleggende betingelser for rutinen.")


                if init_forutsetninger_sjekk:


                    # Finner oversikt over gjennomførte tiltak, kan brukes til betingede endringer/ tiltak
                    # Lager liste med gjennomførte tiltak
                    gjennomforteTiltak = []

                    arcpy.SelectLayerByLocation_management(tiltakLYR, "within", geo, '', 'NEW_SELECTION')

                    with arcpy.da.SearchCursor(tiltakLYR, ["STATUS", "STATE", "OBJECTID"]) as cursor:
                        for row in cursor:
                            if row[0] == 2 and row[1] == 1 :
                                gjennomforteTiltak.append(hentVerdierBestand(tiltakLYR, row[2]))

                    arcpy.SelectLayerByAttribute_management(tiltakLYR, "CLEAR_SELECTION")

                    dict_external_write = copy.deepcopy(dict_external)
                    if valgt_rutine[u'endringer'].has_key(u'endring_bestand'):
                        if valgt_rutine[u'endringer'][u'endring_bestand'].has_key(u'generelle_endringer'):
                            if valgt_rutine[u'endringer'][u'endring_bestand'][u'generelle_endringer'].has_key(u'attributtliste'):
                                att_liste = valgt_rutine[u'endringer'][u'endring_bestand'][u'generelle_endringer'][u'attributtliste']
                                for att in att_liste:
                                    if dict_external_write.has_key(att['felt']):
                                        if att[u'endring'] == u'Absolutt verdi':
                                            dict_external_write[att[u'felt']] = att[u'verdi']
                                        elif att[u'endring'] == u'Blank':
                                            dict_external_write[att[u'felt']] = None
                                        elif att[u'endring'] == u'Funksjon':
                                            uttrykk = evaluering_oppdatering.Uttrykk(unicode(att[u'verdi']),dict_internal,dict_external_write)
                                            beregnet = evaluering_oppdatering.evaluerTre(uttrykk)
                                            if beregnet[0]:
                                                dict_external_write[att[u'felt']] = beregnet[1]
                                        elif att[u'endring'] == u'Tabell':
                                            #TODO Mangler feilhåndtering
                                            #TODO Sender med gjennomførte tiltak her, kun til bruk i tabelloppslag. Kan etterhvert skrives om så det brukes via "Funksjon"...
                                            oppslag = evaluering_oppdatering.tabellOppslag(dict_external, dict_internal, att[u'verdi'],gjennomforteTiltak, filnavn_konfig)
                                            dict_external_write[att[u'felt']] = oppslag



                                        if att.has_key(u'log_beskrivelse'):
                                            beskr_tekst = att[u'log_beskrivelse']
                                            beskr_tekst = beskr_tekst.replace("%%",unicode(dict_external_write[att[u'felt']]))
                                            pr(beskr_tekst)


                        if valgt_rutine[u'endringer'][u'endring_bestand'].has_key(u'betingede_endringer'):
                            for bet in valgt_rutine[u'endringer'][u'endring_bestand'][u'betingede_endringer']:
                                if bet.has_key(u'betingelser'):
                                    uttrykk = evaluering_oppdatering.Uttrykk(bet[u'betingelser'],dict_internal,dict_external_write)
                                    beregnet = evaluering_oppdatering.evaluerTre(uttrykk)
                                    if beregnet[0]:
                                        if beregnet[1]:
                                            pr("Bestandet innfrir folgende betingelser: " + bet[u'betingelser'])
                                            if bet.has_key(u'attributtliste'):
                                                att_liste = bet[u'attributtliste']
                                                for att in att_liste:
                                                    if dict_external_write.has_key(att['felt']):
                                                        if att[u'endring'] == u'Absolutt verdi':
                                                            dict_external_write[att[u'felt']] = att[u'verdi']
                                                        elif att[u'endring'] == u'Blank':
                                                            dict_external_write[att[u'felt']] = None
                                                        elif att[u'endring'] == u'Funksjon':
                                                            uttrykk = evaluering_oppdatering.Uttrykk(unicode(att[u'verdi']),dict_internal,dict_external_write)
                                                            beregnet = evaluering_oppdatering.evaluerTre(uttrykk)
                                                            if beregnet[0]:
                                                                dict_external_write[att[u'felt']] = beregnet[1]


                                                        if att.has_key(u'log_beskrivelse'):
                                                            beskr_tekst = att[u'log_beskrivelse']
                                                            beskr_tekst = beskr_tekst.replace("%%",unicode(dict_external_write[att[u'felt']]))
                                                            pr(beskr_tekst)

                                        else:
                                            pr("Bestandet innfrir IKKE folgende betingelser: " + bet[u'betingelser'])

                    ant_endringer = 0
                    ut_liste= list(best_row)
                    fields = cur_bestand.fields
                    for field in fields:
                        if dict_external_write.has_key("!" + field +"!"):
                            if dict_external_write["!" + field +"!"] != dict_external["!" + field +"!"]:
                                ant_endringer+=1
                                ut_liste[cur_bestand.fields.index(field)] = dict_external_write["!" + field +"!"]
                    if ant_endringer>0:
                        cur_bestand.updateRow(ut_liste)




                    # Tiltak
                    
                    #SLETT GAMLE FORESLÅTTE TILTAK

                    if slettTiltak:
                        #pr("Sletter gamle tiltak")
                        arcpy.SelectLayerByLocation_management(tiltakLYR, "within", geo, '', 'NEW_SELECTION')

                        #Sletter foreslåtte tiltak uten order-id
                        with arcpy.da.UpdateCursor(tiltakLYR, ["STATUS", "ORDER_ID", "STATE", "OBJECTID"]) as cursor:
                            for row in cursor:
                                if row[0] == 1 and row[1] == None:
                                    pr("Setter tiltak " + str(row[3])+ " state til deleted")
                                    row[2] = 0
                                    cursor.updateRow(row)

                        arcpy.SelectLayerByAttribute_management(tiltakLYR, "CLEAR_SELECTION")

                    if valgt_rutine[u'endringer'].has_key(u'nye_tiltak'):
                        liste_nye_tiltak = valgt_rutine[u'endringer'][u'nye_tiltak']
                        arcpy.CreateFeatureclass_management("in_memory","Temp_TILTAK","POLYGON",template=tiltakLYR)



                        #GENERELLE TILTAK
                        if liste_nye_tiltak.has_key(u'generelle_tiltak'):
                            for gen_tiltak in liste_nye_tiltak[u'generelle_tiltak'][u'tiltaksliste']:
                                #print gen_tiltak
                                list_attributter = list()
                                for att in gen_tiltak.keys():
                                    #at_d =gen_tiltak[att]
                                    if unicode(gen_tiltak[att]).count("?")>0 or unicode(att).count("+")>0 or unicode(att).count("-")>0 or unicode(att).count("/")>0 or unicode(att).count("*")>0 :
                                        uttrykk = evaluering_oppdatering.Uttrykk(gen_tiltak[att],dict_internal,dict_external)
                                        ber_uttrykk = evaluering_oppdatering.evaluerTre(uttrykk)
                                        if ber_uttrykk[0]:
                                            gen_tiltak[att] = ber_uttrykk[1]

                                #a = lag_tiltak(layer_tiltak,gen_tiltak['type'],gen_tiltak['prioritet'],1,gen_tiltak['aarstall'],"",gen_tiltak['arealandel'],geo)
                                pr("Lager generelt tiltak i bestand OID:" + str(oid_verdi) + " : " + gen_tiltak['kommentar'])
                                a = lag_tiltak(os.path.join("in_memory","Temp_TILTAK"),gen_tiltak['type'],gen_tiltak['prioritet'],1,gen_tiltak['aarstall'],"",gen_tiltak['arealandel'],geo,hovednummer=dict_external_write['!HOVEDNR!'],bestandid=dict_external_write['!BESTAND_ID!'],eiendomid=dict_external_write['!EIENDOM_ID!'])
                                #a = lag_tiltak(allma_tiltaklag,gen_tiltak['type'],gen_tiltak['prioritet'],1,2020,"",gen_tiltak['arealandel'],geo)

                        #BETINGEDE TILTAK
                        if liste_nye_tiltak.has_key(u'betingede_tiltak'):
                            for bet_tiltak in liste_nye_tiltak[u'betingede_tiltak']:
                                betingelse = bet_tiltak['betingelser']
                                uttrykk = evaluering_oppdatering.Uttrykk(betingelse,dict_internal,dict_external)
                                ber_betingelse = evaluering_oppdatering.evaluerTre(uttrykk)
                                if ber_betingelse[0] and ber_betingelse[1]:
                                    for tilt in bet_tiltak[u'tiltaksliste']:
                                        for att in tilt.keys():
                                            #at_d =gen_tiltak[att]
                                            if unicode(tilt[att]).count("?")>0 or unicode(att).count("+")>0 or unicode(att).count("-")>0 or unicode(att).count("/")>0 or unicode(att).count("*")>0 :
                                                uttrykk = evaluering_oppdatering.Uttrykk(tilt[att],dict_internal,dict_external)
                                                ber_uttrykk = evaluering_oppdatering.evaluerTre(uttrykk)
                                                if ber_uttrykk[0]:
                                                    tilt[att] = ber_uttrykk[1]

                                        #a = lag_tiltak(layer_tiltak,gen_tiltak['type'],gen_tiltak['prioritet'],1,gen_tiltak['aarstall'],"",gen_tiltak['arealandel'],geo)
                                        pr("Lager betinget tiltak i bestand OID: " + str(oid_verdi) + " : " + betingelse + " " +tilt['kommentar'])
                                        a = lag_tiltak(os.path.join("in_memory","Temp_TILTAK"),tilt['type'],tilt['prioritet'],1,tilt['aarstall'],"",tilt['arealandel'],geo,hovednummer=dict_external_write['!HOVEDNR!'],bestandid=dict_external_write['!BESTAND_ID!'],eiendomid=dict_external_write['!EIENDOM_ID!'])
                                        #a = lag_tiltak(allma_tiltaklag,gen_tiltak['type'],gen_tiltak['prioritet'],1,2020,"",gen_tiltak['arealandel'],geo)





                        arcpy.Append_management(os.path.join("in_memory","Temp_TILTAK"),tiltakLYR,schema_type="NO_TEST")
                        #arcpy.Append_management()

                        arcpy.Delete_management(os.path.join("in_memory","Temp_TILTAK"))



            del cur_bestand
edit.stopOperation()
edit.stopEditing(True)


##    for r in rutiner:
##        print r[u'rutinenavn']
##        print r[u'endringer'][u'nye_tiltak'][u'generelle_tiltak']
##        print str(r)
##
##        #if p==
##        #for g in data['endringer']:
##        #    print str(g)