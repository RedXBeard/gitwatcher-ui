from shortcuts import findparent
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    path = ""
    screen = None
    def __init__(self, path, screen):
        self.path = path
        self.screen = screen

    def on_any_event(self, event):
        if self.path == event.src_path:
            from main import RepoWatcher

            root = findparent(self.screen, RepoWatcher)

            if root.history_button.pressed:
                self.screen.check_history(self.path)

            elif root.changes_button.pressed:
                self.screen.changes_check(self.path)

            elif root.branches_button.pressed:
                self.screen.branches_check(self.path)

            elif root.settings_button.pressed:
                self.screen.settings_check(self.path)


