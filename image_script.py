# enter directory path
import os
import datetime
import shutil
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path


# function to perform copying
def rename_files_with_creation_date(copy_from_directory, copy_to_directory):
	
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

			jpg_directory = copy_to_directory / date_folder
			raw_file_sub_directory = jpg_directory / 'raw'

			# create root folder and raw subdir if they don't exist
			if date_folder not in created_dirs:
				Path.mkdir(jpg_directory, exist_ok=True)
				Path.mkdir(raw_file_sub_directory, exist_ok=True)

				created_dirs.add(date_folder)
				# print(f"created directories {jpg_directory} and {raw_file_sub_directory}")

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

	# print(f"Copied {jpg_count} JPEG files and {raw_count} Raw files.")

# function to choose directories
def pick_directory(title: str) -> Path | None:
	path_str = filedialog.askdirectory(title=title)
	return Path(path_str) if path_str else None

# rename_files_with_creation_date(copy_from_directory_path, copy_to_directory_path)

# INTERFACE!!!!!!!!!!!!!!!!

root = Tk()
root.title("Image Copier")

copy_from = None
copy_to = None

mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

from_label = StringVar()
to_label = StringVar()

def choose_source():
	global copy_from
	copy_from = pick_directory("Select Source Folder")
	if copy_from:
		from_label.set(str(copy_from))
	update_run_button_state()

def choose_destination():
	global copy_to
	copy_to = pick_directory("Select Destination Folder")
	if copy_to:
		to_label.set(str(copy_to))
	update_run_button_state()

def run_copy():
	if not copy_from or not copy_to:
		print("Please select both folders first")
		return
	rename_files_with_creation_date(copy_from, copy_to)

def update_run_button_state():
	if copy_from and copy_to:
		run_button.state(["!disabled"])
	else:
		run_button.state(["disabled"])

ttk.Button(mainframe, text="Choose Source Folder", command=choose_source).grid(column=0, row=1, sticky=W)
ttk.Label(mainframe, text="Source Directory: ").grid(column=1, row=1, sticky=W)
ttk.Label(mainframe, textvariable=from_label, wraplength=200, justify="left").grid(column=2, row=1, sticky=EW)

ttk.Button(mainframe, text="Choose Destination Folder", command=choose_destination).grid(column=0, row=2, sticky=EW)
ttk.Label(mainframe, text="Destination Directory: ").grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, textvariable=to_label, wraplength=200, justify="left").grid(column=2, row=2, sticky=W)

run_button = ttk.Button(mainframe, text="Run", command=run_copy, state="disabled")
run_button.grid(column=3, row=4, sticky=(S, E))



root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(0, weight=0)
mainframe.columnconfigure(1, weight=0)
mainframe.columnconfigure(2, weight=1, minsize=200)
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()