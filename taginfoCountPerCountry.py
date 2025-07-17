#!/usr/bin/env -S uv run python
import argparse
import asyncio
from dataclasses import dataclass

import httpx
from tqdm.asyncio import tqdm


class LANG:
    PL = "pl"
    EN = "en"


class ISO:
    WORLD = "WORLD"
    EUROPE = "EUROPE"


class NORMALIZE:
    POPULATION = "population"
    AREA = "area"


@dataclass(frozen=True)
class Country:
    nameEn: str
    namePl: str
    taginfo: str
    isoCode: str

    @property
    def symbol(self):
        match self.isoCode:
            case ISO.WORLD:
                return ":world_map:"
            case ISO.EUROPE:
                return ":flag-eu:"
            case _:
                return f":flag-{self.isoCode.lower()}:"

    @property
    def host(self):
        if self.isoCode == ISO.WORLD:
            return "https://taginfo.openstreetmap.org/"
        return f"https://taginfo.geofabrik.de/{self.taginfo}/"


COUNTRIES = {
    Country("World", "Świat", "", ISO.WORLD),
    Country("Europe", "Europa", "europe", ISO.EUROPE),
    Country("Poland", "Polska", "europe:poland", "PL"),
    Country("Germany", "Niemcy", "europe:germany", "DE"),
    Country("France", "Francja", "europe:france", "FR"),
    Country("Spain", "Hiszpania", "europe:spain", "ES"),
    Country("UK", "UK", "europe:united-kingdom", "GB"),
    Country("Italy", "Włochy", "europe:italy", "IT"),
    Country("Czechia", "Czechy", "europe:czech-republic", "CZ"),
    Country("Russia", "Rosja", "russia", "RU"),
    Country("Turkey", "Turcja", "europe:turkey", "TR"),
    Country("Ukraine", "Ukraina", "europe:ukraine", "UA"),
    Country("Romania", "Rumunia", "europe:romania", "RO"),
    Country("Netherlands", "Holandia", "europe:netherlands", "NL"),
    Country("Slovakia", "Słowacja", "europe:slovakia", "SK"),
    Country("Belgium", "Belgia", "europe:belgium", "BE"),
    Country("Hungary", "Węgry", "europe:hungary", "HU"),
    Country("Austria", "Austria", "europe:austria", "AT"),
    Country("Belarus", "Białoruś", "europe:belarus", "BY"),
    Country("Lithuania", "Litwa", "europe:lithuania", "LT"),
    Country("Canada", "Kanada", "north-america:canada", "CA"),
    Country("USA", "USA", "north-america:us", "US"),
    Country("Brazil", "Brazylia", "south-america:brazil", "BR"),
    Country("China", "Chiny", "asia:china", "CN"),
    Country("Japan", "Japonia", "asia:japan", "JP"),
}

client = httpx.AsyncClient()


@dataclass
class TaginfoResult:
    label: str
    count: int
    isoCode: str


async def taginfoCount(
    key: str, value: str, host: str, label: str, isoCode: str
) -> TaginfoResult:
    response = await client.get(f"{host}api/4/tag/stats?key={key}&value={value}")
    response.raise_for_status()
    return TaginfoResult(label, response.json()["data"][0]["count"], isoCode)


@dataclass
class WikidataResult:
    population: int
    area: int


async def queryWikidata():
    countryIsoCodes = "({})".format(
        ", ".join(
            [
                f'"{country.isoCode}"'
                for country in COUNTRIES
                if country.isoCode not in (ISO.WORLD, ISO.EUROPE)
            ]
        )
    )
    queryCountries = f"""
    SELECT ?item ?isoCode ?population ?area WHERE {{
      ?item wdt:P1082 ?population.
      ?item wdt:P2046 ?area.
      ?item wdt:P297 ?isoCode.
      FILTER(?isoCode IN {countryIsoCodes})
    }}"""
    querySpecials = f"""
    SELECT ?item ?isoCode ?population ?area WHERE {{
      ?item wdt:P1082 ?population.
      ?item wdt:P2046 ?area.
      FILTER(?item IN (wd:Q2, wd:Q46))
      BIND(IF(?item=wd:Q2, "{ISO.WORLD}", "{ISO.EUROPE}") AS ?isoCode).
    }}"""
    query = f"""
        SELECT * {{
        {{
            {queryCountries}
        }} 
        UNION 
        {{
            {querySpecials}
        }} 
        }} ORDER BY DESC(?population)
    """
    response = await client.get(
        "https://query.wikidata.org/sparql", params={"query": query, "format": "json"}
    )
    response.raise_for_status()
    return response.json()


async def getWikidataResults() -> dict[str, WikidataResult]:
    data = await queryWikidata()
    results = {}
    for item in data["results"]["bindings"]:
        isoCode = item["isoCode"]["value"]
        population = int(float(item["population"]["value"]))
        area = int(float(item["area"]["value"]))
        results[isoCode] = WikidataResult(population, area)
    return results


async def main():
    parser = argparse.ArgumentParser(prog="taginfoCountPerCountry")
    parser.add_argument("key")
    parser.add_argument("value")
    parser.add_argument(
        "--lang", default=LANG.EN, choices=[LANG.EN, LANG.PL], required=False
    )
    parser.add_argument(
        "--normalize", choices=[NORMALIZE.AREA, NORMALIZE.POPULATION], required=False
    )
    parser.add_argument("--symbol", default=False, required=False, action="store_true")
    args = parser.parse_args()
    results: list[TaginfoResult] = await tqdm.gather(
        *[
            taginfoCount(
                args.key,
                args.value,
                country.host,
                f"{country.symbol + ' ' if args.symbol else ''}"
                + f"{country.nameEn if args.lang == LANG.EN else country.namePl}",
                country.isoCode,
            )
            for country in COUNTRIES
        ],
        desc="↔️ Checking taginfo",
    )
    resultsPerIso = {result.isoCode: result for result in results}
    if args.normalize:
        wikidataResults = await getWikidataResults()
        for isoCode in wikidataResults:
            value = (
                wikidataResults[isoCode].population
                if args.normalize == NORMALIZE.POPULATION
                else wikidataResults[isoCode].area
            )
            print(f"iso {isoCode}, ratio {value}, count {resultsPerIso[isoCode].count}")
            resultsPerIso[isoCode].count = int(
                1_000_000 * resultsPerIso[isoCode].count / value
            )
    output = sorted(list(resultsPerIso.values()), key=lambda x: x.count, reverse=True)
    for result in output:
        print(f"{result.label}: {result.count}")


if __name__ == "__main__":
    asyncio.run(main())
