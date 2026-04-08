import datetime
import exifread
import shutil
import threading
from tkinter import *
from tkinter import ttk, filedialog
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2", ".orf"}
JPG_EXTENSIONS = {".jpg", ".jpeg"}
RAW_EXTENSIONS = {".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2", ".orf"}

class CopyJob:
	def __init__(self, source: Path, destination: Path):
		self.image = source
		self.date_created = self._get_date_created(self.image)
		self.new_filename = self._generate_new_filename(self.image, self.date_created)
		self.destination_directory = self._make_destination_directory(self.date_created, destination)

	def _get_date_created(self, image):
		with open(image, 'rb') as file:
			exif_data = exifread.process_file(file, stop_tag='DateTimeOriginal', details=False, extract_thumbnail=False)
			time_stamp = exif_data.get("EXIF DateTimeOriginal")
			
			try:
				date_created = datetime.datetime.strptime(str(time_stamp), "%Y:%m:%d %H:%M:%S")
			except ValueError:
				time_stamp = image.stat().st_mtime
				date_created = datetime.datetime.fromtimestamp(time_stamp)

				print(f"{image} lacked exif data - copied with file timestamp")
				
		
		return date_created

	def _generate_new_filename(self, image, date_created):

		new_filename = f"{date_created.strftime('%Y_%m_%d')}_{image.name}"
		
		return new_filename

	def _make_destination_directory(self, date_created, destination):
		
		if self.image.suffix.lower() in JPG_EXTENSIONS:
			destination_directory = destination / date_created.strftime('%Y_%m')
		else:
			destination_directory = destination / date_created.strftime('%Y_%m') / 'raw'
		
		return destination_directory



class ImageCopier:

	def __init__(self, source: Path, destination: Path, progress_cb=None):
		self.source = source
		self.destination = destination
		self.progress_cb = progress_cb
		
	def run(self):

		images = [image for image in self.source.iterdir() if image.is_file() and image.suffix.lower() in SUPPORTED_EXTENSIONS]
		# total X 2 to account for ImageCopier and then copying
		total = len(images)
		done = 0

		created_directories = set()
		
		for image in images:
			copy_job = CopyJob(image, self.destination)
			self._ensure_directories(copy_job.destination_directory, created_directories)
			self._copy_image(copy_job.image, copy_job.destination_directory, copy_job.new_filename)
			done += 1
			if self.progress_cb:
				self.progress_cb(done, total)

	
	def _ensure_directories(self, directory, created_directories):
		if directory not in created_directories:
			directory.mkdir(parents=True, exist_ok=True)
			
			created_directories.add(directory)

	
	def _copy_image(self, image, destination_directory, new_filename):
		# if image.suffix.lower() == ".jpg" or image.suffix.lower() == ".jpeg":
		target_path = destination_directory / new_filename
		shutil.copy2(image, target_path)

class ImageDeleter:

	def __init__(self, directory: Path, progress_cb=None):
		self.directory = directory
		self.raw_directory = directory / 'raw'
		self.progress_cb = progress_cb

	def run(self):
		jpgs = {file.stem for file in self.directory.iterdir() if file.is_file() and file.suffix.lower() in JPG_EXTENSIONS}
		
		raw_files = [file for file in self.raw_directory.iterdir() if file.is_file() and file.suffix.lower() in RAW_EXTENSIONS]

		total = len(raw_files) - len(jpgs)
		done = 0

		for file in raw_files:
			if file.stem not in jpgs:
				file.unlink(missing_ok=True)
			done += 1
			if self.progress_cb:
				self.progress_cb(done, total)




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