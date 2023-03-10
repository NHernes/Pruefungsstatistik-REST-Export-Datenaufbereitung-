import json, datetime, requests,sys, pandas as pd, schedule, time
from pathlib import Path
import mimetypes
fachbereiche=["bcp","erzpsy","vetmed","wiwiss","physik","jfk","geowiss","polsoz","philgeist","sz","rewiss","geschkult","matheinf","mi"]
semester_alle={
    "wise1920":"Wintersemester 19/20","sose 2020":"Sommersemester 2020","sose2020":"Sommersemester 2020","sose20":"Sommersemester 2020","sose-2020":"Sommersemester 2020","sosoe2020":"Sommersemester 2020",

    "wise20-21":"Wintersemester 2020/2021","wise20-21":"Wintersemester 2020/2021","wise2021":"Wintersemester 2020/2021","wise 2020/2021":"Wintersemester 2020/2021","wise2021":"Wintersemester 2020/2021","ws-20-21":"Wintersemester 2020/2021","wise-2020-2021":"Wintersemester 2020/2021","ws2020-2021":"Wintersemester 2020/2021","wise 2020-2021":"Wintersemester 2020/2021","wise2020-2021":"Wintersemester 2020/2021","wise-20-21":"Wintersemester 2020/2021","ws2021":"Wintersemester 2020/2021","ws20-21":"Wintersemester 2020/2021","wise2020-2021":"Wintersemester 2020/2021","wise-2021":"Wintersemester 2020/2021","ws-2021":"Wintersemester 2020/2021","wise2020":"Wintersemester 2020/2021","wisee20/21":"Wintersemester 2020/2021",

    "21-sose":"Sommersemester 2021",

    "21-wise":"Wintersemester 2021/2022","wise21/22":"Wintersemester 2021/2022",

    "22-sose":"Sommersemester 2022","sose-22":"Sommersemester 2022","sose2022":"Sommersemester 2022",

    "22-wise":"Wintersemester 2022/2023","wise2022-2023":"Wintersemester 2022/2023",

    "23-sose":"Sommersemester 2023",

    "23-wise":"Wintersemester 2023/2024"
    }

semesterzuordnung={
            "Sommersemester 2020":{"Start":"2020-06-01","Ende":"2020-11-30"},
            "Wintersemester 2020/2021":{"Start":"2020-12-01","Ende":"2021-05-31"},
            "Sommersemester 2021":{"Start":"2021-06-01","Ende":"2021-11-30"},
            "Wintersemester 2021/2022":{"Start":"2021-12-01","Ende":"2022-05-31"},
            "Sommersemester 2022":{"Start":"2022-06-01","Ende":"2022-11-30"},
            "Wintersemester 2022/2023":{"Start":"2022-12-01","Ende":"2023-05-31"},
            "Sommersemester 2023":{"Start":"2023-06-01","Ende":"2023-11-30"},
            "Wintersemester 2023/2024":{"Start":"2023-12-01","Ende":"2024-05-31"},
            }

#depricated function
def daten_exportieren():
    def oauth():
        lplus_client_id= ''
        lplus_client_secret= ''
        benutzername=''
        passwort=''


        payload = {
            'grant_type': 'password',
            'client_id': lplus_client_id,
            'client_secret': lplus_client_secret,
            'username': benutzername,
            'password': passwort}
        r = requests.post('https://fub.lplus-teststudio.de/token', data=payload)
        token=json.loads(r.text)['access_token']
        return token

    def get_licences(token):
        demolizenzen=["e-examinations@home","zusatz","showcase","html","take-home","workshop","mp3","rth-","videotest","funktionstests","e-examinations@home om","lts5","zusatz-lts5testlizenz","drag-drop","neue lizenz","test api","test-impact","gjpa","demokatalog","testlizenz","julia","test_freigabe","heptner","test_bug","kopie","tali","testkatalog","_testlizenz_22","inaktiv","charit??","cedis","demopr??fung","doz","probe"]

        headers={
            "Authorization": f"Bearer {token}"
            }

        r = requests.get('https://fub.lplus-teststudio.de/publicapi/v1/licences',headers=headers)
        lizensen=json.loads(r.text)

        datengrundlage_lizenzen_tagesaktuell=[]
        for lizenz in lizensen:
            zu_pr??fende_lizenz=lizenz["name"].lower()
            if any(lizenz in zu_pr??fende_lizenz for lizenz in demolizenzen):
                pass
            else:
                lizenzpaar={"Name":lizenz["name"],"ID":lizenz["id"]}
                datengrundlage_lizenzen_tagesaktuell.append(lizenzpaar)

        
        print(datengrundlage_lizenzen_tagesaktuell)
        print(len(datengrundlage_lizenzen_tagesaktuell))
        return datengrundlage_lizenzen_tagesaktuell

    def get_subject(token,datengrundlage_lizenzen_tagesaktuell):
        demof??cher=["demopr??fung","doz","probe","cedis"]

        headers={
            "Authorization": f"Bearer {token}"
            }
        
        z??hler=0
        checker=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            z??hler+=1
            if checker<z??hler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
                
            lizenz_id=lizenz["ID"]
            r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects',headers=headers)
            f??cher=json.loads(r.text)

            #print(f"F??cher: {f??cher}","\n")
            
            f??cher_core=[]
            for listeneintrag in f??cher:
                if any(demofach in listeneintrag["name"].lower() for demofach in demof??cher):
                    pass
                else:
                    if " HK" in listeneintrag["name"] or "hauptklausur" in listeneintrag["name"].lower():
                        durchgang="HK"
                    elif " NK" in listeneintrag["name"] or "nachklausur" in listeneintrag["name"].lower() or "wiederholungsklausur" in listeneintrag["name"].lower():
                        durchgang = "NK"
                    else:
                        durchgang = None
                        
                    eintrag={"Fach-ID":listeneintrag["id"],"Fachname":listeneintrag["name"],"Pr??fungsdurchgang":durchgang}
                    f??cher_core.append(eintrag)
            lizenz["F??cher"]=f??cher_core
            print(f"F??cher {z??hler}")         

        return datengrundlage_lizenzen_tagesaktuell
        
    def get_exam_enrollment_and_tries(datengrundlage_lizenzen_tagesaktuell):
        token=oauth()
        headers={
        "Authorization": f"Bearer {token}"
        }

        z??hler=0
        checker=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            z??hler+=1
            if checker<z??hler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
            
            lizenz_id=lizenz["ID"]
            
            datum_heute=datetime.datetime.today().date()
            for fach in lizenz["F??cher"]:
                fach_id=fach["Fach-ID"]
                fach["Semester"]=[]

                for semester, datum in semesterzuordnung.items():
                    semester_aktuell=semester

                    datum_start=datum["Start"]
                    datum_ende=datum["Ende"]

                    if datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() <= datum_heute:
                    
                        url=f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/{fach_id}/statistics?dateFilterData.dateFrom={datum_start}&dateFilterData.dateTo={datum_ende}'

                        r = requests.get(url,headers=headers)
                        
                        statistik=json.loads(r.text)

                        pr??fungsdurchf??hrungen=statistik["candidatesWithExaminationTries"]

                        fach["Semester"].append({semester_aktuell:{"Absolvierte Pr??fungen": pr??fungsdurchf??hrungen}})


                print(fach)                   
            
            #print(f"Absolvierte Pr??fungen {z??hler}")
        
        return datengrundlage_lizenzen_tagesaktuell
  

    def hinzuf??gen_von_metadaten(datengrundlage_lizenzen_tagesaktuell):
        for lizenz in datengrundlage_lizenzen_tagesaktuell:

            name_lizenz=lizenz["Name"].lower()
            for fb in fachbereiche:
                if fb in name_lizenz:
                    lizenz["Fachbereich"]=fb
                    break
            else:
                lizenz["Fachbereich"]=None

            """   
            for semester_idio,semester_generisch in semester_alle.items():
                if semester_idio in name_lizenz:
                    lizenz["Semester"]=semester_generisch
                    break
            else:
                lizenz["Semester"]=None
            """

            if "EEC" in lizenz["Name"]:
                lizenz["Format"] = "Pr??senz"
            elif "HOME" in lizenz["Name"]:
                lizenz["Format"] = "Distanz"
            else:
                lizenz["Format"] = None
        
        return datengrundlage_lizenzen_tagesaktuell

    #Eigentliche Methode
    token=oauth() #Token generieren
    
    datengrundlage_lizenzen_tagesaktuell=get_licences(token) #Alle Lizenzen auf Plattform ziehen
    datengrundlage_lizenzen_tagesaktuell=get_subject(token,datengrundlage_lizenzen_tagesaktuell) #Zugeh??rige F??cher der Lizenzen ziehen

    datengrundlage_lizenzen_tagesaktuell=get_exam_enrollment_and_tries(datengrundlage_lizenzen_tagesaktuell) #Gemeldete und gepr??fte Studierende ziehen

    datengrundlage_lizenzen_tagesaktuell=hinzuf??gen_von_metadaten(datengrundlage_lizenzen_tagesaktuell) #Fachbereich und Semester zu Lizenz hinzuf??gen
    print(datengrundlage_lizenzen_tagesaktuell)
    
    return datengrundlage_lizenzen_tagesaktuell

# 1. Schritt: Tagesaktuelle Daten der Plattform ziehen
def daten_exportieren_current_semester():
    
    def oauth():
        lplus_client_id= ''
        lplus_client_secret= ''
        benutzername=''
        passwort=''


        payload = {
            'grant_type': 'password',
            'client_id': lplus_client_id,
            'client_secret': lplus_client_secret,
            'username': benutzername,
            'password': passwort}
        r = requests.post('https://fub.lplus-teststudio.de/token', data=payload)
        token=json.loads(r.text)['access_token']
        return token

    def get_licences(token):
        demolizenzen=["e-examinations@home","zusatz","showcase","html","take-home","workshop","mp3","rth-","videotest","funktionstests","e-examinations@home om","lts5","zusatz-lts5testlizenz","drag-drop","neue lizenz","test api","test-impact","gjpa","demokatalog","testlizenz","julia","test_freigabe","heptner","test_bug","kopie","tali","testkatalog","_testlizenz_22","inaktiv","charit??","cedis","demopr??fung","doz","probe"]

        headers={
            "Authorization": f"Bearer {token}"
            }

        connection_counter=0
        while connection_counter < 5:
            try:
                r = requests.get('https://fub.lplus-teststudio.de/publicapi/v1/licences',headers=headers)
                lizensen=json.loads(r.text)
                break
            except:
                connection_counter+=1
                time.sleep(connection_counter)
        else:
            sys.exit()

        datengrundlage_lizenzen_tagesaktuell=[]
        for lizenz in lizensen:
            zu_pr??fende_lizenz=lizenz["name"].lower()
            if any(lizenz in zu_pr??fende_lizenz for lizenz in demolizenzen):
                pass
            else:
                lizenzpaar={"Name":lizenz["name"],"ID":lizenz["id"]}
                datengrundlage_lizenzen_tagesaktuell.append(lizenzpaar)

        print(len(datengrundlage_lizenzen_tagesaktuell))
        return datengrundlage_lizenzen_tagesaktuell

    def check_licence_change(liste_aktuelle_lizenzen, datengrundlage_lizenzen):
        print("Beginne Pr??fung ??nderung von Lizenznamen")
        
        for eintrag in datengrundlage_lizenzen:
            for inhalt in liste_aktuelle_lizenzen:
                if eintrag["ID"] == inhalt["ID"]:
                    if eintrag["Name"] != inhalt["Name"]:
                        eintrag["Name"] = inhalt["Name"]
        
        return datengrundlage_lizenzen

    def check_subject_change(datengrundlage_lizenzen):
        print("Beginne Pr??fung auf ??nderung von Fachnamen und neu angelegte F??cher")
        demof??cher=["demopr??fung","doz","probe","cedis"]
        z??hler=0
        checker=0
        counter=0
        for eintrag in datengrundlage_lizenzen:
            counter+=1
            print(f"Abfrage Nr. {counter}")

            z??hler+=1
            if checker<z??hler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")

            lizenz_id=eintrag["ID"]

            connection_counter=0
            while connection_counter < 5:
                try:
                    r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/',headers=headers)
                    f??cher=json.loads(r.text)
                    break
                
                except:
                    connection_counter+=1
                    time.sleep(connection_counter)
                    print(fach)
            else:
                sys.exit()
            
            drop_liste_f??cher=[]
            for fach in eintrag["F??cher"]:
                fach_id=fach["Fach-ID"]
                fach_name=fach["Fachname"]
                
                
                for response in f??cher: 
                    if response["id"] == fach_id:
                        drop_liste_f??cher.append(response)

                        if response["name"] != fach_name:
                            fach["Fachname"] = response["name"]
                
            #print(drop_liste_f??cher,"\n")

            for eintrag2 in drop_liste_f??cher:
                if eintrag2 in f??cher:
                    f??cher.remove(eintrag2)
            
            for response in f??cher:
                if any(demofach in response["name"].lower() for demofach in demof??cher):
                    pass
                else:
                    eintrag["F??cher"].append({"Fach-ID":response["id"],"Fachname":response["name"],"Pr??fungsdurchgang":None})
                    print(eintrag)

                
                            



        return datengrundlage_lizenzen

    def compare_saved_and_new_lincences(alte_liste,aktuelle_liste):
        print("Vergleiche Datenbank und neue Daten")
        liste_hinzuzuf??gender_lizenzen=[]

        for lizenz in aktuelle_liste:
            for alte_lizenz in alte_liste:
                if lizenz["ID"] in alte_lizenz.values():
                    break
            else:
                liste_hinzuzuf??gender_lizenzen.append(lizenz)
        
        print(liste_hinzuzuf??gender_lizenzen)
        return liste_hinzuzuf??gender_lizenzen

    def get_new_subjects(liste_neuer_lizenzen):
        print("Ziehe neue F??cherdaten")

        demof??cher=["demopr??fung","doz","probe","cedis"]
        
        z??hler=0
        checker=0
        for lizenz in liste_neuer_lizenzen:
            z??hler+=1
            if checker<z??hler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
                
            lizenz_id=lizenz["ID"]

            connection_counter=0
            while connection_counter < 5:
                try:
                    r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects',headers=headers)
                    f??cher=json.loads(r.text)
                    break
                except:
                    connection_counter+=1
                    time.sleep(connection_counter)
            else:
                sys.exit()


            
            f??cher_core=[]
            for listeneintrag in f??cher:
                if any(demofach in listeneintrag["name"].lower() for demofach in demof??cher):
                    pass
                
                else:    
                    eintrag={"Fach-ID":listeneintrag["id"],"Fachname":listeneintrag["name"],"Pr??fungsdurchgang":None}
                    f??cher_core.append(eintrag)
            lizenz["F??cher"]=f??cher_core
     

        return liste_neuer_lizenzen
  
    def merge_lists(liste_neuer_lizenzen, datengrundlage_lizenzen):
        print("Kombiniere Datenbank mit neuen Daten")
        print(liste_neuer_lizenzen)
        if len(liste_neuer_lizenzen)>0:
            datengrundlage_lizenzen=datengrundlage_lizenzen+liste_neuer_lizenzen
        else:
            pass

        return datengrundlage_lizenzen

    def hinzuf??gen_von_metadaten(datengrundlage_lizenzen):
        print("F??ge Metadaten hinzu")
        for lizenz in datengrundlage_lizenzen:

            name_lizenz=lizenz["Name"].lower()
            for fb in fachbereiche:
                if fb in name_lizenz:
                    lizenz["Fachbereich"] = fb
                    break
            else:
                lizenz["Fachbereich"]="MISC"

            if "EEC" in lizenz["Name"]:
                lizenz["Format"] = "Pr??senz"
            elif "HOME" in lizenz["Name"]:
                lizenz["Format"] = "Distanz"
            else:
                lizenz["Format"] = None

            for fach in lizenz["F??cher"]:
                if " HK" in fach["Fachname"] or "hauptklausur" in fach["Fachname"].lower():
                        fach["Pr??fungsdurchgang"] = "HK"

                elif " NK" in fach["Fachname"] or "nachklausur" in fach["Fachname"].lower() or "wiederholungsklausur" in fach["Fachname"].lower():
                        fach["Pr??fungsdurchgang"] =  "NK"
                else:
                    fach["Pr??fungsdurchgang"] = None


        return datengrundlage_lizenzen
   
    def get_exam_enrollment_and_tries_of_current_semester(datengrundlage_lizenzen_tagesaktuell):
        print("Ziehe aktuelle Pr??fungszahlen")

        token=oauth()
        headers={
        "Authorization": f"Bearer {token}"
        }

        z??hler=0
        checker=0
        counter=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            z??hler+=1
            if checker<z??hler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
            
            #print(lizenz)
            lizenz_id=lizenz["ID"]
            
            datum_heute=datetime.datetime.today().date()
            
            
            for fach in lizenz["F??cher"]:
                counter+=1
                print(f"Abfrage Nr. {counter}")
                
                fach_id=fach["Fach-ID"]

                if not fach.get("Semester"):
                    fach["Semester"]=[]
               
                for semester, datum in semesterzuordnung.items():

                    semester_aktuell=semester

                    datum_start=datum["Start"]
                    datum_ende=datum["Ende"]

                    if datum_heute > datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() and datum_heute > datetime.datetime.strptime(datum_ende, "%Y-%m-%d").date():
                        
                        for eintrag in fach["Semester"]:
                            if eintrag.get(semester):
                                break
                        else:
                            print("Noch keine Daten f??r das vergangene Semester vorliegend - ersetze mit 0.")
                            fach["Semester"].append({semester_aktuell:{"Absolvierte Pr??fungen": 0}})


                    elif datum_heute >= datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() and datum_heute <= datetime.datetime.strptime(datum_ende, "%Y-%m-%d").date():
    
                        url=f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/{fach_id}/statistics?dateFilterData.dateFrom={datum_start}&dateFilterData.dateTo={datum_ende}'
                        
                        connection_counter=0
                        while connection_counter < 5:
                            try:
                                r = requests.get(url,headers=headers)
                                statistik=json.loads(r.text)
                                pr??fungsdurchf??hrungen=statistik["candidatesWithExaminationTries"]
                        
                                for eintrag in fach["Semester"]:
                                    semester_json=list(eintrag.keys())[0]
                                    if semester_json == semester:
                                        break
                                else:
                                    fach["Semester"].append({semester:""})
                                
                                for sem in fach["Semester"]:
                                    for key, item in sem.items():
                                        if key == semester:
                                            sem[key]={"Absolvierte Pr??fungen": pr??fungsdurchf??hrungen}
                                        break
                                break
                            
                            except ValueError:
                                print("Konnte JSON nicht dekodieren")
                                break

                            except:
                                connection_counter+=1
                                time.sleep(connection_counter)
                                print(fach)
                        else:
                            sys.exit()
                        



                    elif datum_heute < datetime.datetime.strptime(datum_start, "%Y-%m-%d").date():
                        pass

        
        return datengrundlage_lizenzen_tagesaktuell

    def filter_leere_lizenzen(datengrundlage_lizenzen_tagesaktuell):
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            liste_eintr??ge_drop=[]
            for eintrag in lizenz["F??cher"]:
                print(eintrag)
                pr??fungsteilnahmen=0
                for inhalt in eintrag["Semester"]:
                    for k,v in inhalt.items():
                        for keys, absolvierte_pr??fungen in v.items(): 
                            pr??fungsteilnahmen=pr??fungsteilnahmen+int(absolvierte_pr??fungen)
                if pr??fungsteilnahmen == 0:
                    liste_eintr??ge_drop.append(eintrag)
            for i in liste_eintr??ge_drop:
                lizenz["F??cher"].remove(i)

        return datengrundlage_lizenzen_tagesaktuell

    #Reinladen der Datenbank
    f = open('pr??fungsdaten_roh_vollst??ndig.json',encoding='utf-8')
    datengrundlage_lizenzen = json.load(f)

    #Erstmaliges Generieren LPLUS Token
    token=oauth()

    #Ziehen der aktuellen Lizenzen
    liste_aktuelle_lizenzen = get_licences(token)

    #Pr??fung auf Namens??nderung der gespeicherten Lizenzen
    datengrundlage_lizenzen = check_licence_change(liste_aktuelle_lizenzen, datengrundlage_lizenzen)
    
    #Pr??fung auf Namens??nderung in gespeicherten F??chern
    datengrundlage_lizenzen = check_subject_change(datengrundlage_lizenzen)

    #Filtern der neu dazugekommenen Lizenzen
    liste_neuer_lizenzen = compare_saved_and_new_lincences(datengrundlage_lizenzen, liste_aktuelle_lizenzen)

    #Ziehen der F??cher f??r neue Lizenzen
    liste_neuer_lizenzen = get_new_subjects(liste_neuer_lizenzen)
    
    #Zusammenf??hrung bestehender Daten und neu generierter Daten
    datengrundlage_lizenzen = merge_lists(liste_neuer_lizenzen, datengrundlage_lizenzen)

    #Hinzuf??gen von Metadaten (Format, Pr??fungsdurchgang, Fachbereich)
    datengrundlage_lizenzen = hinzuf??gen_von_metadaten(datengrundlage_lizenzen)
    
    #Abfrage aktueller Pr??fungsteilnahmen
    datengrundlage_lizenzen_tagesaktuell = get_exam_enrollment_and_tries_of_current_semester(datengrundlage_lizenzen)
    
    #Droppen aller leeren Lizenzen
    #datengrundlage_lizenzen_tagesaktuell = filter_leere_lizenzen(datengrundlage_lizenzen_tagesaktuell)
    #R??ckgabe des vollst??ndigen, aktualisierten Datenstamms
    return datengrundlage_lizenzen_tagesaktuell
    
# 2. Schritt aktuelle Daten mit Datenbank abgleichen
def generierung_datenbank(datengrundlage_lizenzen_tagesaktuell):
    
    #Generieren der Detailansicht aller F??cher
    print("Generiere Daten??bersicht")

    columns=['Fach',"Fach-ID","Lizenz","Lizenz-ID","Fachbereich","Pr??fungsdurchgang","Format"]
    for key,value in semesterzuordnung.items():
        columns.append(key)

    detailtable_f??cher = pd.DataFrame(columns=columns)
    
    sammlung_rows=[]
    for lizenz in datengrundlage_lizenzen_tagesaktuell:
        for fach in lizenz["F??cher"]:
            new_row = {'Fach':fach["Fachname"],"Fach-ID":fach["Fach-ID"],"Lizenz":lizenz["Name"],"Lizenz-ID":lizenz["ID"],"Fachbereich":lizenz["Fachbereich"],"Pr??fungsdurchgang":fach["Pr??fungsdurchgang"],"Format":lizenz["Format"]}
            for key,value in semesterzuordnung.items():
                for eintrag in fach["Semester"]:
                    if eintrag.get(key):
                        new_row[key]=eintrag[key]["Absolvierte Pr??fungen"]
            sammlung_rows.append(new_row)
    
    detailtable_f??cher = pd.DataFrame(sammlung_rows)

    #detailtable_f??cher = pd.concat([detailtable_f??cher,new_rows], ignore_index=True)
    print(detailtable_f??cher)

    detailtable_f??cher.to_csv("F??cherliste.csv", encoding="utf-8-sig", sep=";")

    #Generieren der ??bersicht der Pr??fungszahlen nach Semester und Fachbereich

    columns=["Fachbereiche"]
    for key,value in semesterzuordnung.items():
        columns.append(key)
    
    #Fachbereiche eintragen
    fachbereiche.sort()
    fachbereiche.append("MISC")


    gesamt??bersicht_pr??fungszahlen = pd.DataFrame(columns=columns)
    gesamt??bersicht_pr??fungszahlen["Fachbereiche"]=fachbereiche
    gesamt??bersicht_pr??fungszahlen=gesamt??bersicht_pr??fungszahlen.set_index('Fachbereiche')

    #Analyse der Detailstatistik f??r Semester-Pr??fungszahlen 
    #Analyse der jeweiligen Semester

    for semester in semesterzuordnung.keys():
        analyse_dict={}
        for fb in fachbereiche:
            dict_paar={fb:0}
            analyse_dict.update(dict_paar)
        analyse_dict.update({"MISC":0})
        analyse_dict_aktuell=analyse_dict

        for key, value in analyse_dict_aktuell.items():
            try:
                dftest=detailtable_f??cher.loc[detailtable_f??cher['Fachbereich'] == key, semester]

                analyse_dict_aktuell[key]=dftest.sum()
                value=dftest.sum()
            except:
                pass
        for key,value in analyse_dict_aktuell.items():
            gesamt??bersicht_pr??fungszahlen.loc[[key],[semester]] = value


    gesamt??bersicht_pr??fungszahlen = gesamt??bersicht_pr??fungszahlen.fillna(0)
    gesamt??bersicht_pr??fungszahlen.loc["Total"] = gesamt??bersicht_pr??fungszahlen.sum()
    gesamt??bersicht_pr??fungszahlen['Total'] = gesamt??bersicht_pr??fungszahlen.sum(axis=1)
    print(gesamt??bersicht_pr??fungszahlen)

    gesamt??bersicht_pr??fungszahlen.to_excel("Gesamt??bersicht Pr??fungszahlen.xlsx", encoding="utf-8-sig")
                

# 3. Schritt: Upload ins Wiki
def upload_wiki():
    print("Laden Daten??bersicht in Wiki hoch")

    zielseite=""
    token=""
    url = f'https://wikis.fu-berlin.de/rest/api/content/{zielseite}/child/attachment/'
    headers = {"Authorization": f"Bearer {token}"}
    
    
    r = requests.get(url, headers=headers)
    attachment_id=json.loads(r.text)
    attachment_id=attachment_id["results"][0]["id"]
    
    url = f'https://wikis.fu-berlin.de/rest/api/content/{zielseite}/child/attachment/{attachment_id}/data'
    headers = {'X-Atlassian-Token': 'no-check',
               "Authorization": f"Bearer {token}"}
    file = 'Gesamt??bersicht Pr??fungszahlen.xlsx'

    # determine content-type
    content_type, encoding = mimetypes.guess_type(file)
    if content_type is None:
        content_type = 'multipart/form-data'

    # provide content-type explicitly
    files = {'file': (file, open(file, 'rb'), content_type)}

    r = requests.post(url, headers=headers, files=files)

    if r.status_code==200:
        print("Datei erfolgreich hochgeladen")
    else:
        print("Achtung, Fehler beim Upload")

####Ablauf Skript mit Abfrage aktuelles Semester
def include_all():
    
    datengrundlage_lizenzen_tagesaktuell=daten_exportieren_current_semester()
    
    with open('pr??fungsdaten_roh_vollst??ndig.json', 'w') as f: #
        json.dump(datengrundlage_lizenzen_tagesaktuell, f)  #data is dumped into file 
    
    cwd = Path.cwd()
    
    with open(f'{cwd}/repository/{datetime.datetime.today().date().strftime("%Y-%m-%d")}_pr??fungsdaten_roh_vollst??ndig.json', 'w') as f: #
        json.dump(datengrundlage_lizenzen_tagesaktuell, f)  #data is dumped into file 
        
    generierung_datenbank(datengrundlage_lizenzen_tagesaktuell)
    
    upload_wiki()


schedule.every().day.at("00:00").do(include_all)

while True:

    schedule.run_pending()
    
    time.sleep(1)

