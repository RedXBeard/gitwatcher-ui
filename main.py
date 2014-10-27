import os
import json
import settings
from time import time
from kivy.app import App
from kivy.lang import Builder, Parser, ParserException

from kivy.properties import ListProperty, StringProperty, \
                            NumericProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner

from shortcuts import run_syscall, striptags, create_popup, diff_formatter, findparent
from listitems import RepoItem, RepoHistoryItem, ChangesItem, \
                      UnPushedItem, BranchesItem, DiffItem
from buttons import *
from boxlayouts import *

from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '1')

cmd = "echo $HOME"
out = run_syscall(cmd)
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()

KVS = os.path.join(settings.PROJECT_PATH, "assets/themes")
CLASSES = [c[:-3] for c in os.listdir(KVS) if c.endswith('.kv') ]
ICON_PATH = os.path.join(settings.PROJECT_PATH, 'assets/icon') + 'gitwatcher-ui_icon.png'


class CustomLabel(Label):
    pass

class CustomSpinner(Spinner):
    def _on_dropdown_select(self, instance, data, *largs):
        self.text = "[b]%s[/b]"%data
        self.is_open = False

        root = findparent(self, RepoWatcher)
        root.change_branch(data, self.path)


class Menu(BoxLayout):

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        parser = Parser(content=open(self.kv_file).read())
        widget = Factory.get(parser.root.name)()
        Builder._apply_rule(widget, parser.root, parser.root)
        self.add_widget(widget)

    @property
    def kv_file(self):
        return os.path.join(KVS, self.__class__.__name__ + '.kv')

for class_name in CLASSES:
    globals()[class_name] = type(class_name, (Menu,), {})


class RepoWatcher(BoxLayout):
    repos = ListProperty()
    history = ListProperty()
    active_menu_button = StringProperty()
    screen_manager = ObjectProperty()

    pb = ProgressBar()

    def __init__(self, *args, **kwargs):
        super(BoxLayout, self).__init__(*args, **kwargs)
        self.active_menu_button = "changes"
        self.show_kv('Changes')

    def show_kv(self, value):
        if value == "FileDiff":
            self.screen_manager.transition = SlideTransition(direction='right')
        else:
            self.screen_manager.transition = SlideTransition(direction='left')

        prev = self.screen_manager.current
        self.screen_manager.current = value
        child = self.screen_manager.current_screen.children[0]

        selected_menu_class = child.children[0].__class__
        repolist = self.repolstview.children[0].children[0].children
        pressed_repo = filter(lambda x: x.repobut.pressed, repolist)
        if pressed_repo:
            if selected_menu_class == ChangesBox().__class__:
                child.children[0].changes_check(pressed_repo[0].repo_path)

            elif selected_menu_class == HistoryBox().__class__:
                keep_old = False
                if prev == 'FileDiff':
                    keep_old = True
                child.children[0].check_history(pressed_repo[0].repo_path,
                                                keep_old = keep_old)

            elif selected_menu_class == BranchesBox().__class__:
                child.children[0].branches_check(pressed_repo[0].repo_path)

            elif selected_menu_class == SettingsBox().__class__:
                child.children[0].settings_check(pressed_repo[0].repo_path)


    def args_converter(self, row_index, item):
        return {
            'repo_index': row_index,
            'repo_path': item['path'],
            'repo_name': item['name']}

    def load_repo(self):
        try:
            repofile = file(REPOFILE, "r")
            self.repos = json.loads(repofile.read())
            repofile.close()
            self.history = []
            if self.screen_manager.current == "History":
                screen = self.screen_manager.children[0].children[0].children[0]
                screen.history = []
        except (IOError, TypeError, ValueError):
            self.repos = []
            self.history = []

    def get_activebranch(self, path):
        os.chdir(path)
        out = run_syscall('git branch')
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
        os.chdir(settings.PROJECT_PATH)
        return text

    def get_branches(self, path, callback=None):
        os.chdir(path)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = self.get_activebranch(path)
        self.branchlist.text = "[b]%s[/b]"%text
        self.branchlist.values = values
        self.branchlist.path = path
        self.branchlist.font_name = settings.KIVY_DEFAULT_FONT
        os.chdir(settings.PROJECT_PATH)
        if callback:
            callback()

    def change_branch(self, branch_name, path):
        try:
            branch_name = striptags(branch_name)
            os.chdir(path)
            out = run_syscall('git stash clear;git stash;git checkout %s;git stash pop' % branch_name)
            screen = self.screen_manager.children[0].children[0].children[0]
            if self.screen_manager.current == "History":
                screen.check_history(path)
            elif self.screen_manager.current == "Changes":
                screen.changes_check(path)
            elif self.screen_manager.current == "Branches":
                screen.branches_check(path)
            elif self.screen_manager.current == 'Settings':
                screen.settings_check(path)
        except OSError:
            pass
        finally:
            os.chdir(settings.PROJECT_PATH)


class RepoWatcherApp(App):
    def build(self):
        self.title = "Repo Watcher"
        self.icon = ICON_PATH
        Builder.load_file('assets/themes/Compact.kv')

        layout = RepoWatcher()
        layout.load_repo()

        return layout

    def load_repo(self):
        self.layout.load_repo()

    def load_history(self):
        self.layout.load_history()


if __name__ == '__main__':
    RepoWatcherApp().run()
