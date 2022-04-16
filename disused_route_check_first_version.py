#!/usr/bin/env python3
from disused_route import downloadDisusedRoutes
import requests


def checkFirstVersionOfRoutes(routes):
    for route in routes:
        data = requests.get(
            f"https://www.openstreetmap.org/api/0.6/relation/{route.id}/1.json"
        ).json()
        tags = data["elements"][0]["tags"]
        print(tags["type"], f"https://osm.org/relation/{route.id}", tags["name"])


disusedRoutes = downloadDisusedRoutes()
checkFirstVersionOfRoutes(disusedRoutes)
