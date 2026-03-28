import datetime
import exifread
import shutil
import threading
from tkinter import *
from tkinter import ttk, filedialog

from pathlib import Path

class ImageCopier:

	def __init__(self, source: Path, destination: Path, progress_cb=None):
		self.source = source
		self.destination = destination
		self.progress_cb = progress_cb
		
	def run(self):

		supported_extensions = {".jpg", "jpeg", ".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2", ".orf"}

		images = [image for image in self.source.iterdir() if image.is_file() and image.suffix.lower() in supported_extensions]
		total = len(images)
		done = 0

		created_dirs = set()
		
		for image in images:
			self._process_file(image, created_dirs)
			done += 1
			if self.progress_cb:
				self.progress_cb(done, total)

	def _process_file(self, image: Path, created_dirs: set):
		jpg_directory, raw_directory, date_created, date_folder = self._get_target_directories(image)
		self._ensure_directories(date_folder, jpg_directory, raw_directory, created_dirs)
		new_filename = self._build_filename(image, date_created)	
		self._copy_image(image, jpg_directory, raw_directory, new_filename)
	
	def _get_target_directories(self, image: Path):

		# fetch date created from exif data
		with open(image, 'rb') as file:
			exif_data = exifread.process_file(file, stop_tag='DateTimeOriginal', details=False, extract_thumbnail=False)
			time_stamp = exif_data.get("EXIF DateTimeOriginal")
		# convert to datetime object
		date_created = datetime.datetime.strptime(str(time_stamp), "%Y:%m:%d %H:%M:%S")
		
		date_folder = date_created.strftime('%Y_%m')
	
		jpg_directory = self.destination / date_folder
		raw_directory = jpg_directory / 'raw'

		return jpg_directory, raw_directory, date_created, date_folder

	def _ensure_directories(self, date_folder: str, jpg_directory: Path, raw_directory: Path, created_dirs: set):
		if date_folder not in created_dirs:
			jpg_directory.mkdir(parents=True, exist_ok=True)
			raw_directory.mkdir(parents=True, exist_ok=True)
			
			created_dirs.add(date_folder)

	def _build_filename(self, image: Path, date_created: datetime.datetime):
		new_filename = f"{date_created.strftime('%Y_%m_%d')}_{image.name}"

		return new_filename
	
	def _copy_image(self, image, jpg_directory, raw_directory, new_filename):
		if image.suffix.lower() == ".jpg" or image.suffix.lower() == ".jpeg":
			target_path = jpg_directory / new_filename
			shutil.copy2(image, target_path)

		else:
			target_path = raw_directory / new_filename
			shutil.copy2(image, target_path)

class ImageCopierUI:
	
	def __init__(self):
		self.root = Tk()
		self.root.title("Image Copier")	

		self.copy_from = None
		self.copy_to = None

		self.from_label = StringVar()
		self.to_label = StringVar()
		
		self.progress_var = DoubleVar(value=0.0)
		self.progress_fraction = 0.0
		self._worker_running = False

		self._build_widgets()

	def _build_widgets(self):
		self.mainframe = ttk.Frame(self.root, padding=(3, 3, 12, 12))
		self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
				 
		ttk.Button(self.mainframe, text="Choose Source Folder", command=self._choose_source).grid(column=0, row=1, sticky=W)
		ttk.Label(self.mainframe, text="Source Directory: ").grid(column=1, row=1, sticky=W)
		ttk.Label(self.mainframe, textvariable=self.from_label, wraplength=200, justify="left").grid(column=2, row=1, sticky=EW)

		ttk.Button(self.mainframe, text="Choose Destination Folder", command=self._choose_destination).grid(column=0, row=2, sticky=EW)
		ttk.Label(self.mainframe, text="Destination Directory: ").grid(column=1, row=2, sticky=W)
		ttk.Label(self.mainframe, textvariable=self.to_label, wraplength=200, justify="left").grid(column=2, row=2, sticky=W)

		ttk.Label(self.mainframe, text="Progress").grid(column=0, row=3, sticky=(W))
		
		self.progress_bar = ttk.Progressbar(
			self.mainframe,
			orient='horizontal',
			mode='determinate',
			variable=self.progress_var, 
			maximum=1.0
		)
		self.progress_bar.grid(column=0, columnspan=3, row=4, sticky=(W, E))

		self.run_button = ttk.Button(self.mainframe, text="Run", command=self._run_copy, state="disabled")
		self.run_button.grid(column=3, row=6, sticky=(S, E))

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)
		self.mainframe.columnconfigure(0, weight=0)
		self.mainframe.columnconfigure(1, weight=0)
		self.mainframe.columnconfigure(2, weight=1, minsize=200)
		for child in self.mainframe.winfo_children():
			child.grid_configure(padx=5, pady=5)
		
	def _choose_source(self):
		self.copy_from = self.pick_directory("Select Source Folder")
		if self.copy_from:
			self.from_label.set(str(self.copy_from))
		self._update_run_button_state()

	def _choose_destination(self):
		self.copy_to = self.pick_directory("Select Destination Folder")
		if self.copy_to:
			self.to_label.set(str(self.copy_to))
		self._update_run_button_state()

	def pick_directory(self, title: str) -> Path | None:
		path_str = filedialog.askdirectory(title=title)
		return Path(path_str) if path_str else None
	
	def _run_copy(self):
		if not self.copy_from or not self.copy_to:
			print("Please select both folders first")
			return
		copier = ImageCopier(self.copy_from, self.copy_to, progress_cb=self._on_progress)

		self._worker_running = True

		threading.Thread(target=self._run_worker, args=(copier,), daemon=True).start()

		self._poll_progress()

	def _update_run_button_state(self):
		if self.copy_from and self.copy_to:
			self.run_button.state(["!disabled"])
		else:
			self.run_button.state(["disabled"])

	def _on_progress(self, done, total):
		if total == 0:
			self.progress_fraction = 1.0
		else:
			self.progress_fraction = done / total	

	def _poll_progress(self):
		self.progress_var.set(self.progress_fraction)

		if self._worker_running:
			self.root.after(50, self._poll_progress)
		else:
			self.progress_var.set(1.0)
	
	def run(self):
		self.root.mainloop()

	def _run_worker(self, copier):
		copier.run()
		self._worker_running = False

if __name__ == "__main__":
    app = ImageCopierUI()
    app.run()