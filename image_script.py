# enter directory path
import os
import datetime
import shutil

def rename_files_with_creation_date(copy_from_directory, base_copy_to_directory):
	for filename in os.listdir(copy_from_directory):
		source = os.path.join(copy_from_directory, filename)
		# this check is needed in order to ignore directories
		if os.path.isfile(source):
			# next line is not readable as a date by humans
			creation_time = os.path.getctime(source)
			# make timestamp readable
			date_created = datetime.datetime.fromtimestamp(creation_time)
			date_folder = date_created.strftime('%Y_%m')

			target_directory = os.path.join(base_copy_to_directory, date_folder)
			os.makedirs(target_directory, exist_ok=True)

			new_filename = f"{date_created.strftime('%Y_%m_%d')}_{filename}"
			destination = os.path.join(target_directory, new_filename)

			shutil.copy2(source, destination)
			print(f"Copied '{filename}' to '{destination}'")

copy_from_directory_path = "/volumes/RICOH GR/DCIM/100RICOH"
base_copy_to_directory_path = "/Users/zachlarabee/pictures"

rename_files_with_creation_date(copy_from_directory_path, base_copy_to_directory_path)



