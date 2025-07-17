#!/usr/bin/env -S uv run python
from itertools import groupby
import overpy


def downloadDisusedRoutes():
    query = """
        area["name"="Warszawa"]["admin_level"=6];
        (
            relation["disused:route"]["name"](area);
        );
        out center;
    """
    overpassResult = overpy.Overpass().query(query)
    return overpassResult.relations


def disusedRouteType(route):
    return route.tags["disused:route"]


if __name__ == "__main__":
    disusedRoutes = downloadDisusedRoutes()
    for vehicle, routes in groupby(
        sorted(disusedRoutes, key=disusedRouteType), key=disusedRouteType
    ):
        print()
        print(vehicle)
        for route in sorted(list(routes), key=lambda route: route.tags["name"]):
            print(route.tags["name"], f"https://osm.org/relation/{route.id}")
