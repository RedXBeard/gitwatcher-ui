from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    path = ""
    screen = None
    def __init__(self, path, screen):
        self.path = path
        self.screen = screen

    def on_any_event(self, event):
        if self.path == event.src_path:
            print "ok"
            self.screen.branches_check(self.path)


