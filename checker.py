from shortcuts import findparent
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    path = ""
    root = None
    def __init__(self, path, root):
        self.path = path
        self.root = root

    def on_any_event(self, event):
        if self.path in event.src_path:
            self.root.refresh_required(self.path)
