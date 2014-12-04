from shortcuts import findparent
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    path = ""
    root = None
    def __init__(self, path, root):
        self.path = path
        self.root = root

    def on_any_event(self, event):
    	# Some paths should be ignored as .git directory
    	ignore = False
    	if event.src_path.find('.git') != -1:
        	ignore = True
        if not ignore and self.path in event.src_path :
            self.root.refresh_required(self.path)
    