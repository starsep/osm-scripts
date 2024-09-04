#!/usr/bin/env python
import argparse
import asyncio

import httpx
from tqdm.asyncio import tqdm


LANG_PL = "pl"
LANG_EN = "en"

COUNTRIES = {
    ("World", "Świat", "https://taginfo.openstreetmap.org/", ":world_map:"),
    ("Europe", "Europa", "https://taginfo.geofabrik.de/europe/", ":flag-eu:"),
    ("Poland", "Polska", "https://taginfo.geofabrik.de/europe:poland/", ":flag-pl:"),
    ("Germany", "Niemcy", "https://taginfo.geofabrik.de/europe:germany/", ":flag-de:"),
    ("France", "Francja", "https://taginfo.geofabrik.de/europe:france/", ":flag-fr:"),
    ("Spain", "Hiszpania", "https://taginfo.geofabrik.de/europe:spain/", ":flag-es:"),
    ("UK", "UK", "https://taginfo.geofabrik.de/europe:united-kingdom/", ":flag-gb:"),
    ("Italy", "Włochy", "https://taginfo.geofabrik.de/europe:italy/", ":flag-it:"),
    (
        "Czechia",
        "Czechy",
        "https://taginfo.geofabrik.de/europe:czech-republic/",
        ":flag-cz:",
    ),
    ("Russia", "Rosja", "https://taginfo.geofabrik.de/russia/", ":flag-ru:"),
    ("Turkey", "Turcja", "https://taginfo.geofabrik.de/europe:turkey/", ":flag-tr:"),
    ("Ukraine", "Ukraina", "https://taginfo.geofabrik.de/europe:ukraine/", ":flag-ua:"),
    ("Romania", "Rumunia", "https://taginfo.geofabrik.de/europe:romania/", ":flag-ro:"),
    (
        "Netherlands",
        "Holandia",
        "https://taginfo.geofabrik.de/europe:netherlands/",
        ":flag-nl:",
    ),
    (
        "Slovakia",
        "Słowacja",
        "https://taginfo.geofabrik.de/europe:slovakia/",
        ":flag-sk:",
    ),
    ("Belgium", "Belgia", "https://taginfo.geofabrik.de/europe:belgium/", ":flag-be:"),
    ("Hungary", "Węgry", "https://taginfo.geofabrik.de/europe:hungary/", ":flag-hu:"),
    ("Austria", "Austria", "https://taginfo.geofabrik.de/europe:austria/", ":flag-at:"),
    ("Belarus", "Białoruś", "https://taginfo.geofabrik.de/europe:belarus/", ":flag-by:"),
    ("Lithuania", "Litwa", "https://taginfo.geofabrik.de/europe:lithuania/", ":flag-lt:"),
    ("Canada", "Kanada", "https://taginfo.geofabrik.de/north-america:canada/", ":flag-ca:"),
    ("USA", "USA", "https://taginfo.geofabrik.de/north-america:us/", ":flag-us:"),
    ("Brazil", "Brazylia", "https://taginfo.geofabrik.de/south-america:brazil/", ":flag-br:"),
    ("China", "Chiny", "https://taginfo.geofabrik.de/asia:china/", ":flag-cn:"),
    ("Japan", "Japonia", "https://taginfo.geofabrik.de/asia:japan/", ":flag-jp:"),
}

client = httpx.AsyncClient()


async def taginfoCount(key: str, value: str, host: str, label: str) -> tuple[str, int]:
    response = await client.get(f"{host}api/4/tag/stats?key={key}&value={value}")
    response.raise_for_status()
    return label, response.json()["data"][0]["count"]


async def main():
    parser = argparse.ArgumentParser(prog="taginfoCountPerCountry")
    parser.add_argument("key")
    parser.add_argument("value")
    parser.add_argument(
        "--lang", default=LANG_EN, choices=[LANG_EN, LANG_PL], required=False
    )
    parser.add_argument("--symbol", default=False, required=False, action="store_true")
    args = parser.parse_args()
    langIndex = 0 if args.lang == LANG_EN else 1
    results = await tqdm.gather(
        *[
            taginfoCount(
                args.key,
                args.value,
                host,
                f"{symbol + ' ' if args.symbol else ''}{(nameEn, namePl)[langIndex]}",
            )
            for (nameEn, namePl, host, symbol) in COUNTRIES
        ],
        desc="↔️ Checking taginfo",
    )
    results = sorted(results, key=lambda x: x[1], reverse=True)
    for result in results:
        print(f"{result[0]}: {result[1]}")


if __name__ == "__main__":
    asyncio.run(main())
