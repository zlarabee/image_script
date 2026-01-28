# enter directory path
import os
import datetime
import shutil

from pathlib import Path

copy_from_directory_path = Path("/volumes/RICOH GR/DCIM/100RICOH")
# copy_from_directory_path = Path("/Users/zachlarabee/pictures/test")
base_copy_to_directory_path = Path("/Users/zachlarabee/pictures")

def rename_files_with_creation_date(copy_from_directory, base_copy_to_directory):
	
	# track which directories are being created so shorten run time. 
	created_dirs = set()
	
	jpg_count = 0
	raw_count = 0
	
	for image in copy_from_directory.iterdir():

		if image.is_file():
			
			# get file extension for use later
			file_extension = image.suffix.lower()
	
			# next line is not readable as a date by humans
			creation_time = os.path.getctime(image)

			# make timestamp readable
			date_created = datetime.datetime.fromtimestamp(creation_time)
			date_folder = date_created.strftime('%Y_%m')

			jpg_directory = base_copy_to_directory_path / date_folder
			raw_file_sub_directory = jpg_directory / 'raw'

			# create root folder and raw subdir if they don't exist
			if date_folder not in created_dirs:
				Path.mkdir(jpg_directory, exist_ok=True)
				Path.mkdir(raw_file_sub_directory, exist_ok=True)

				created_dirs.add(date_folder)
				print(f"created directories {jpg_directory} and {raw_file_sub_directory}")

			new_filename = f"{date_created.strftime('%Y_%m_%d')}_{image.name}"

			if file_extension == ".jpg" or file_extension == ".jpeg":

				destination = jpg_directory / new_filename
				shutil.copy2(image, destination)
				jpg_count += 1

			else:
				destination = raw_file_sub_directory / new_filename
				shutil.copy2(image, destination)
				raw_count += 1


			# print(f"Copied '{image}' to '{destination}'")

	print(f"Copied {jpg_count} JPEG files and {raw_count} Raw files.")



rename_files_with_creation_date(copy_from_directory_path, base_copy_to_directory_path)



