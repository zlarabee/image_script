# enter directory path
import os
import datetime
import shutil

from pathlib import Path

copy_from_directory_path = Path("/volumes/RICOH GR/DCIM/100RICOH")
base_copy_to_directory_path = Path("/Users/zachlarabee/pictures")

def rename_files_with_creation_date(copy_from_directory, base_copy_to_directory):
	
	for file in os.listdir(copy_from_directory):
		# source = os.path.join(copy_from_directory, file)
		source = copy_from_directory / file
		# this check is needed in order to ignore directories

		if source.is_file():
			
			# get file extension for use later
			file_extension = source.suffix.lower()
	
			# next line is not readable as a date by humans
			creation_time = os.path.getctime(source)

			# make timestamp readable
			date_created = datetime.datetime.fromtimestamp(creation_time)
			date_folder = date_created.strftime('%Y_%m')

			target_directory = base_copy_to_directory_path / date_folder

			# subfolder for raw files
			raw_file_sub_directory = target_directory / 'raw'
			Path.mkdir(target_directory, exist_ok=True)
			Path.mkdir(raw_file_sub_directory, exist_ok=True)
			# os.makedirs(target_directory, exist_ok=True)
			# os.makedirs(raw_file_sub_directory, exist_ok=True)

			new_filename = f"{date_created.strftime('%Y_%m_%d')}_{file}"
			destination = target_directory / new_filename
			# destination = os.path.join(target_directory, new_filename)

			shutil.copy2(source, destination)
			print(f"Copied '{file}' to '{destination}'")



rename_files_with_creation_date(copy_from_directory_path, base_copy_to_directory_path)



