import datetime
from pathlib import Path
from PIL import Image
import exifread
import json

image = Path.home() / 'pictures/test2' / (input("enter file name: "))
    
with open(image, "rb") as file:

    tags = exifread.process_file(file, stop_tag='DateTimeOriginal', details=False, extract_thumbnail=False)
    time_stamp = tags.get("EXIF DateTimeOriginal")

    try:
        date_created = datetime.datetime.strptime(str(time_stamp), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        time_stamp = image.stat().st_mtime
        date_created = datetime.datetime.fromtimestamp(time_stamp)
        

        print(f"{image} lacked exif data - copied with file timestamp")


    print(tags)
    # print(f'daaaaaaate time {tags["EXIF DateTimeOriginal"]}')
    
    # exif_data = file.getexif()

    # create_date =  exif_data.get(306)
    # create_date2 = exif_data.get(36867)


    # print(f"EXIF: {exif_data}")

    # print(f"306: {create_date}")
    # print(f"36867: {create_date2}")