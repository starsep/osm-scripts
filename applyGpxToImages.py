#!/usr/bin/env -S uv run python

# Requirements:
# argparse
# exif
# gpxpy
# tqdm

import argparse
import datetime
import logging
from pathlib import Path
from typing import Tuple

import gpxpy.gpx
from exif import Image
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="Apply GPS coordinates from GPX file to images"
)
parser.add_argument("gpxFile", type=str, help="Path to gpx file")
parser.add_argument("imagesDir", type=str, help="Path to directory with images")
parser.add_argument(
    "--timeDelta",
    type=int,
    help="Time in seconds between gpx and images",
    default=0,
)
args = parser.parse_args()

gpxPath = Path(args.gpxFile)
imagesDir = Path(args.imagesDir)
timeZoneDelta = datetime.timedelta(hours=2)
gpxImagesDelta = datetime.timedelta(seconds=args.timeDelta)


gpx = gpxpy.parse(gpxPath.open("r"))
timeToCoords = dict()


def replace_tzinfo(dt):
    return dt.replace(tzinfo=None) + timeZoneDelta


for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            time = replace_tzinfo(point.time)
            timeToCoords[time] = point


def coordFloatToDegrees(coord: float) -> Tuple[float, float, float]:
    a = float(int(coord))
    minutes = (coord - a) * 60.0
    b = float(int(minutes))
    c = (minutes - b) * 60.0
    return a, b, c


for image in tqdm(sorted(imagesDir.iterdir())):
    with image.open("rb") as f:
        exifImage = Image(f)
        photoTime = datetime.datetime.strptime(
            exifImage.datetime_original, "%Y:%m:%d %H:%M:%S"
        )
        gpxTime = photoTime + gpxImagesDelta
        if gpxTime not in timeToCoords:
            logging.error(f"Missing time {gpxTime} for photo {image.name}")
            continue
        point = timeToCoords[gpxTime]
        exifImage.gps_latitude = coordFloatToDegrees(point.latitude)
        exifImage.gps_longitude = coordFloatToDegrees(point.longitude)
        exifImage.gps_altitude = point.elevation
        with image.open("wb") as output:
            output.write(exifImage.get_file())
