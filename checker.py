from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print "Got it!"