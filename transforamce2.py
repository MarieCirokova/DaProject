import pandas as pd
df = pd.read_csv('in/tables/STACKING_VYDEJNA_2.csv', index_col='ID', encoding='utf-8')

from haversine import haversine
def maximalni_vzdalenost(objednavky, vydejna):
    """Vraci maximalni vzdalenost od vydejna"""
    max_vzdalenost = -1
    id_vzdalenost = None
    lokace_vzdalenost = None

    for objednavka in objednavky:
        _id = objednavka["id"]
        _lat = objednavka["lat"]
        _long = objednavka["long"]

        lokace_objednavka = (_lat, _long)
        vzdalenost = haversine(vydejna, lokace_objednavka)

        if vzdalenost > max_vzdalenost:
            max_vzdalenost = vzdalenost
            id_vzdalenost = _id
            lokace_vzdalenost = lokace_objednavka

    return id_vzdalenost, max_vzdalenost, lokace_vzdalenost


def nejmensi_vzdalenosti_od(objednavky, lokace_vzdalenost):
    """Od jakeho mista je dvojice (lat,long) nejbliz"""
    seznam_vzdalenosti=[]
    for objednavka in objednavky:
        _id = objednavka["id"]
        _lat = objednavka["lat"]
        _long = objednavka["long"]


        lokace_objednavka = (_lat, _long)
        
        vzdalenost = haversine(lokace_vzdalenost, lokace_objednavka)

        seznam_vzdalenosti.append({"id":_id, "distance":vzdalenost,"lat":round(_lat,3), "long":round(_long,3) })
    serazeny_seznam_vzdalenosti = sorted(seznam_vzdalenosti, key=lambda k: k['distance']) 
    for slovnik in serazeny_seznam_vzdalenosti:
        del slovnik["distance"]
    

    return serazeny_seznam_vzdalenosti[:10]

def vytvor_shluky(objednavky):
    seznam_shluku = []
    idx = objednavky.index
    lat = objednavky["legDestinationLat"]
    long = objednavky["legDestinationLon"]
    vydejna = objednavky[["PICK_UP_LAT", "PICK_UP_LON"]].iloc[0]
    objednavky = [{"id": idx, "lat": lat, "long": long} for idx, lat, long in zip(idx, lat, long)]
    
    while len(objednavky)>0:    
        
        misto_id, max_vzdalenost, lokace_vzdalenost = maximalni_vzdalenost(objednavky, vydejna)
        
        n_prvku_s_nejmensi_vzdalenosti_od = nejmensi_vzdalenosti_od(objednavky, lokace_vzdalenost)
        seznam_shluku.append(n_prvku_s_nejmensi_vzdalenosti_od)
        id_nejmensich_vzdalenosti = [prvek['id'] for prvek in n_prvku_s_nejmensi_vzdalenosti_od]
        
        objednavky = [objednavka for objednavka in objednavky if objednavka['id'] not in 	id_nejmensich_vzdalenosti]
       
    return seznam_shluku
df_groups = df.groupby([ "PICK_UP_PLACE", "DATE_MIDD"])
vysledky_shluky = {}
for group_name, group_df in df_groups:
    seznam_shluku = vytvor_shluky(group_df)
    vysledky_shluky[group_name]=seznam_shluku
    
vystup = []
for vydejna_datetime, baliky in vysledky_shluky.items():
    vydejna, datetime = vydejna_datetime
    for jizda, batch in enumerate(baliky):
        for balik in batch:
            vystup.append({
                "vydejna":vydejna,
                "datetime":datetime,
                "cislo_jizdy":jizda+1,
                "id_baliku":balik["id"],
                "lat_baliku":balik["lat"],
                "lon_baliku":balik["long"]
            })
import csv

with open ("out/tables/vydejna_balicky_output_2.csv", mode="w", newline="") as f:
    writer = csv.DictWriter(f, ["vydejna", "datetime", "cislo_jizdy", "id_baliku", "lat_baliku", "lon_baliku"])
    writer.writeheader()
    for line in vystup:
        writer.writerow(line)