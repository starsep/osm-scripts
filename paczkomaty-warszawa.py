#!/usr/bin/env python3
import geojson
from geojson import FeatureCollection, Feature, Point
import requests
from tqdm import tqdm
import pandas

data = pandas.read_excel("paczkomaty.xlsx")
data = data[data["field_5"] == "Warszawa"]
features = []
for row in tqdm(data.itertuples(), total=len(data)):
    tags = dict(
        amenity="parcel_locker",
        brand="Paczkomat InPost",
        description=row.description,
        operator="InPost",
        parcel_pickup="yes",
        ref=row.ref,
    )
    imageUrl = f"https://geowidget.easypack24.net/uploads/pl/images/{row.ref}.jpg"
    imageResponse = requests.head(imageUrl)
    if imageResponse.status_code == 200:
        tags["image"] = imageUrl
    # else:
    #    print(f"Image error ref={row.ref} status_code={imageResponse.status_code}")
    tags["brand:wikidata"] = "Q110970254"
    tags["brand:wikipedia"] = "pl:InPost"
    tags["operator:wikidata"] = "Q3182097"
    tags["operator:wikipedia"] = "pl:InPost"
    if type(row.opening_hours) == str and len(row.opening_hours) > 0:
        tags["opening_hours"] = row.opening_hours
    if row.parcel_mail_in in {"yes", "no"}:
        tags["parcel_mail_in"] = row.parcel_mail_in
    features.append(
        Feature(geometry=Point((row.field_7, row.field_6)), properties=tags)
    )
geojson.dump(FeatureCollection(features), open("paczkomaty.geojson", "w"))
