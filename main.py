import os
import json
import settings
from kivy.app import App
from kivy.lang import Builder, Parser, ParserException

from kivy.properties import ListProperty, StringProperty, \
                            ObjectProperty
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import SlideTransition
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner

from kivy.uix.widget import WidgetException
from kivy.uix.screenmanager import ScreenManagerException

from shortcuts import run_syscall, striptags, findparent

from buttons import *
from boxlayouts import *

from kivy.config import Config
Config.set('graphics', 'resizable', '1')

Clock.max_iteration = 20

KVS = os.path.join(settings.PROJECT_PATH, "assets/themes")
CLASSES = [c[:-3] for c in os.listdir(KVS) if c.endswith('.kv') ]
ICON_PATH = os.path.join(settings.PROJECT_PATH, 'assets/icon') + 'gitwatcher-ui_icon.png'


class CustomLabel(Label):
    def __del__(self, *args, **kwargs):
        pass


class ConfirmPopup(GridLayout):
    """
    ConfirmPopup is for to handle user input yes-no
    """
    text = StringProperty()

    def __del__(self, *args, **kwargs):
        pass

    def __init__(self,**kwargs):
        self.register_event_type('on_answer')
        super(ConfirmPopup,self).__init__(**kwargs)

    def on_answer(self, *args):
        pass


class CustomSpinner(Spinner):
    """
    Base Spinner class has _on_dropdown_select method which holds
    only change the text attribute of class which is not enough.

    CustomSpinner used to display local branch list so any changes
    of this is actually means changing current branch.
    """

    def __del__(self, *args, **kwargs):
        pass

    def _on_dropdown_select(self, instance, data, *largs):
        self.text = "[b]%s[/b]"%data
        self.is_open = False

        root = findparent(self, RepoWatcher)
        root.change_branch(data, self.path)


class Menu(BoxLayout):
    """
    .kv files are actually classes so each of them should be converted.
    Each .kv files are actually corresponded to a menu button base class
    name chosen as 'Menu'
    """

    def __del__(self, *args, **kwargs):
        pass

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
    """
    RepoWatcher is the based/main class all others generated under this class
    ::repos: repository list which contains all repositories required fields;
        names, paths
    ::active_menu_button: based on the active menu button which are history,
        change, settings and branch screen will change
    ::screen_manager: To handle screen management an attribute will be more
        efficient. By this way there will be no miss
    ::pb: progression can be dislayed

    methods: show_kv, load_repo, get_activebranch, get_branches, change_branch
    """
    repos = ListProperty()
    active_menu_button = StringProperty()
    screen_manager = ObjectProperty()

    pb = ProgressBar()

    def __del__(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        super(BoxLayout, self).__init__(*args, **kwargs)
        self.active_menu_button = "changes"
        self.show_kv('Changes')

    def show_kv(self, value):
        """
        show_kv function is for handle the screen_manager changes
        default was called on init as 'Changes' the names of value
        are represented on main .kv file. Corresponded screen
        in other way to say .kv file displayed.

        ::value: String formatted as 'Changes', 'History', 'Branches',
                'Settings', 'FileDiff'

        In runtime, selected menu button checked for class name, by this way
        screen datas update or keep.
        """
        from boxlayouts import ChangesBox, BranchesBox, SettingsBox, HistoryBox
        try:
            # Transition handled
            if value == "FileDiff":
                self.screen_manager.transition = SlideTransition(direction='right')
            else:
                self.screen_manager.transition = SlideTransition(direction='left')

            # screen changes
            prev = self.screen_manager.current
            self.screen_manager.current = value
            child = self.screen_manager.current_screen.children[0]

            # Menu selection control and related repository tried to find
            selected_menu_class = child.children[0].__class__
            repolist = self.repolstview.children[0].children[0].children
            pressed_repo = filter(lambda x: x.repobut.pressed, repolist)

            # Related screen and repository data merged and screen datas update.
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
            else:
                if selected_menu_class == BranchesBox().__class__:
                    child.children[0].remove_newbranch_widget("")
                    child.children[0].remove_rename_widget("")
        except (WidgetException, ScreenManagerException):
            pass

    def reset_screen(self):
        """
        reset_screen, if repo somehow removed from
            list then screens should be cleared.
        """
        child = self.screen_manager.current_screen.children[0]
        selected_menu_class = child.children[0].__class__

        if selected_menu_class == ChangesBox().__class__:
            child.children[0].changes_check("")

        elif selected_menu_class == HistoryBox().__class__:
            child.children[0].check_history("", keep_old = False)

        elif selected_menu_class == BranchesBox().__class__:
            child.children[0].branches_check("")

        elif selected_menu_class == SettingsBox().__class__:
            child.children[0].settings_check("")


    def args_converter(self, row_index, item):
        """
        args_converter, for displaying repositories
        To display a list of data this convertion style is
        requested for kivy Factory method.
        """
        return {
            'repo_path': item['path'],
            'repo_name': item['name']}

    def load_repo(self):
        """
        load_repo, for loading repository list from .json file (if exists).
        file path is found on settings. In any exception repos sets to empty list
        """
        try:
            repofile = file(settings.REPOFILE, "r")
            self.repos = json.loads(repofile.read())
            repofile.close()
        except (IOError, TypeError, ValueError):
            self.repos = []
        finally:
            self.reset_screen()

    def remove_repo(self, path):
        try:
            repofile = file(settings.REPOFILE, "r")
            repos = json.loads(repofile.read())
            repofile.close()
            repofile = file(settings.REPOFILE, "w")
            self.repos = filter(lambda x: x['path'] != path, repos)
            repofile.write(json.dumps(self.repos))
            repofile.close()
        except (IOError, TypeError, ValueError):
            self.repos = []
        finally:
            self.reset_screen()


    def get_activebranch(self, path):
        """
        get_activebranch, to find the current branch of selected git repository.

        ::path: Repository path
        """
        os.chdir(path)
        out = run_syscall('git branch')
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
        os.chdir(settings.PROJECT_PATH)
        return text

    def get_branches(self, path, callback=None):
        """
        get_branches, collects local branches of repository

        ::path: Repository path.
        ::callback: at the end method calls

        callback method is for to show the progression of bulk of method if any.
        """
        if path:
            os.chdir(path)
            out = run_syscall('git branch')
            values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
            text = self.get_activebranch(path)
            self.branchlist.text = "[b]%s[/b]"%text
            self.branchlist.values = values
            self.branchlist.path = path
            self.branchlist.font_name = settings.KIVY_DEFAULT_FONT
            os.chdir(settings.PROJECT_PATH)
        else:
            self.branchlist.text = ""
            self.branchlist.values = []
            self.branchlist.path = ""
            self.branchlist.font_name = settings.KIVY_DEFAULT_FONT
        if callback:
            callback()

    def change_branch(self, branch_name, path):
        """
        change_branch, handle changing current branches.

        ::branch_name: branch name which wanted to checkout
        ::path: related repository path

        branch name is marked up to use that marup should be cleared
        """
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

    def __del__(self, *args, **kwargs):
        pass

    def build(self):
        """
        Main application object creation, required calls handled
        such title, icon and repository list are sets and
        data collections taken

        ::title: set the title of project
        ::icon: to displayed icon is set

        Builder should be take style, on Mac the same name of
        main application on the same folder will be enough
        but on linux based OS this should be hold by developer
        ::Builder.load_file(...)

        main application 'RepoWatcher' should be hold all
        previously set repository datas, to do that 'load_repo' function called
        """
        self.title = "Git Watcher UI"
        self.icon = ICON_PATH
        Builder.load_file('assets/themes/Compact.kv')

        layout = RepoWatcher()
        layout.load_repo()

        return layout


if __name__ == '__main__':
    RepoWatcherApp().run()
