#!/usr/bin/env python3
from disused_route import downloadDisusedRoutes
import requests


def checkWhenRoutesHaveBeenChangedToDisused(routes):
    print("Routes changed from type=route to type=disused:route")
    for route in routes:
        data = requests.get(
            f"https://www.openstreetmap.org/api/0.6/relation/{route.id}/history.json"
        ).json()
        previousType = "route"
        for version in data["elements"]:
            if "tags" not in version:
                continue
            currentType = version["tags"]["type"]
            if currentType == "disused:route" and previousType == "route":
                print(
                    version["tags"]["name"],
                    version["timestamp"],
                    f"https://osm.org/changeset/{version['changeset']}",
                )
            previousType = currentType
        print()


disusedRoutes = downloadDisusedRoutes()
checkWhenRoutesHaveBeenChangedToDisused(disusedRoutes)
