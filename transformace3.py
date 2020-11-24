import pandas
import csv
from haversine import haversine

dataFrame = pandas.read_csv('in/tables/vydejna_balicky_output_2.csv', encoding='utf-8')

LUZINY = (50.044, 14.332)
ANDEL = (50.074, 14.404)
DEJVICKA = (50.100, 14.392)
HAJE = (50.031, 14.534)

def mamVytvoritNovouJizdu(balicek, predchoziBalicek):
    return balicek['cislo_jizdy'] != predchoziBalicek['cislo_jizdy'] or balicek['vydejna'] != predchoziBalicek['vydejna'] or balicek['datetime'] != predchoziBalicek['datetime']

def vytvorJizdy(dataFrame):
    jizdy = []
    jizda = []
    predchoziBalicek = None
    pocetBalicku = len(dataFrame.index)
    for index, balicek in dataFrame.iterrows():
        if predchoziBalicek is not None and mamVytvoritNovouJizdu(balicek, predchoziBalicek):
            # pokud jsou balíčky z různých jízd, tak "ukončuji" jednu jízdu a zakládám další
            jizdy.append(jizda)
            jizda = []
        elif index == pocetBalicku - 1:
            # pokud se jedná o poslední jízdu z datasetu
            jizdy.append(jizda)

        jizda.append(balicek)
        predchoziBalicek = balicek
    return jizdy
    


def dejMiNejblizsiIndexAVzdalenost(balicky, pocatek, pouziteIndexy):
    minVzdalenost = None
    minVzdalenostIndex = None
    for i in range(len(balicky)):
        if i in pouziteIndexy:
            continue
        balicek = balicky[i]
        vzdalenost = round(haversine((balicek['lat_baliku'], balicek['lon_baliku']), pocatek), 3)
    
        if minVzdalenost is None or vzdalenost < minVzdalenost:
            minVzdalenost = vzdalenost
            minVzdalenostIndex = i

    return (minVzdalenostIndex, minVzdalenost)

def vratPocatecniPolohuBalicku(balicek):
    if balicek['vydejna'] == 'LUZINY':
        return LUZINY
    elif balicek['vydejna'] == 'ANDEL':
        return ANDEL
    elif balicek['vydejna'] == 'DEJVICKA':
        return DEJVICKA
    elif balicek['vydejna'] == 'HAJE':
        return HAJE



def seradIndexyDleVzdalenosti(jizda):    
    pouziteIndexy = [0]
    pocatekJizdy = (jizda[0]['lat_baliku'], jizda[0]['lon_baliku'])
    vzdalenosti = [round(haversine(vratPocatecniPolohuBalicku(jizda[0]), pocatekJizdy), 3)]

    for i in range(len(jizda)):
        nejblizsiIndex, nejblizsiVzdalenost = dejMiNejblizsiIndexAVzdalenost(jizda, pocatekJizdy, pouziteIndexy)

        if nejblizsiIndex is not None:
            pocatekJizdy = (jizda[nejblizsiIndex]['lat_baliku'], jizda[nejblizsiIndex]['lon_baliku'])
            pouziteIndexy.append(nejblizsiIndex)
            vzdalenosti.append(nejblizsiVzdalenost)
    return (pouziteIndexy, vzdalenosti)


def seradBalickyVJizdach(jizdy):
    jizdySeSerazenymiBalicky = []
    indexyVzdalenosti = []
    for jizda in jizdy:
        serazenaJizda = []
        indexyJakSeToMaSeradit, vzdalenosti = seradIndexyDleVzdalenosti(jizda)
        
        for index in range(len(jizda)):
            balicek = jizda[index]
            balicek['poradi'] = indexyJakSeToMaSeradit.index(index) + 1
            balicek['vzdalenost'] = vzdalenosti[indexyJakSeToMaSeradit.index(index)]
            balicek['celkova_vzdalenost'] = sum(vzdalenosti)
            serazenaJizda.append(balicek)

        jizdySeSerazenymiBalicky.append(serazenaJizda)
    return jizdySeSerazenymiBalicky

def upravVystup(jizdySeSerazenymiBalicky):
    vystup = []

    for jizda in jizdySeSerazenymiBalicky:
        for balicek in jizda:
            vystup.append({
                "vydejna": balicek["vydejna"],
                "datetime": balicek["datetime"],
                "cislo_jizdy": balicek["cislo_jizdy"],
                "id_baliku": balicek["id_baliku"],
                "lat_baliku": round(balicek["lat_baliku"], 3),
                "lon_baliku": round(balicek["lon_baliku"], 3),
                "poradi": balicek["poradi"],
                "vzdalenost": round(balicek["vzdalenost"], 3),
                "vzdalenost_odhad":round(balicek["vzdalenost"]*2.374, 3),
                "celkova_vzdalenost": round(balicek["celkova_vzdalenost"], 3),
                "celkova_vzdalenost_odhad":round(balicek["celkova_vzdalenost"]*2.374, 3),
                })
    return vystup


jizdy = vytvorJizdy(dataFrame)
jizdySeSerazenymiBalicky = seradBalickyVJizdach(jizdy)
vystup = upravVystup(jizdySeSerazenymiBalicky)

with open ("out/tables/balicky_output_serazene_2.csv", mode="w", newline="") as f:
    writer = csv.DictWriter(f, ["vydejna", "datetime", "cislo_jizdy", "id_baliku", "lat_baliku", "lon_baliku", "poradi", "vzdalenost", "vzdalenost_odhad", "celkova_vzdalenost", "celkova_vzdalenost_odhad"])
    writer.writeheader()
    for balicek in vystup:
        writer.writerow(balicek)
