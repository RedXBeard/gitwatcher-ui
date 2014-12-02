import os
import json
import settings
from watchdog.observers import Observer

from kivy.app import App
from kivy.core.window import Window
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
from kivy.uix.scatter import Scatter
from kivy.uix.widget import WidgetException
from kivy.uix.screenmanager import ScreenManagerException

from shortcuts import run_syscall, striptags, findparent
from checker import ModifiedHandler
from buttons import *
from boxlayouts import *

Clock.max_iteration = 20

KVS = os.path.join(settings.PROJECT_PATH, "assets%sthemes"%settings.PATH_SEPERATOR)
CLASSES = [c[:-3] for c in os.listdir(KVS) if c.endswith('.kv') ]
ICON_PATH = os.path.join(settings.PROJECT_PATH, 'GitWatcher_typed.ico')


class MyScatter(Scatter):
    name = StringProperty("")
    sha = StringProperty("")
    text = StringProperty("")
    date = StringProperty("")


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


class RemotePopup(GridLayout):
    """
    RemotePopup is for listing all remote names and address for users
    """
    remotes = ListProperty([])
    branch = StringProperty("")

    def __init__(self,**kwargs):
        self.register_event_type('on_push')
        super(RemotePopup,self).__init__(**kwargs)

    def args_converter(self, row_index, item):
        return {
            'remote_path': item['path'],
            'remote_name': item['name']
        }

    def on_push(self, *args):
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
    screen_manager = ObjectProperty()
    pb = ProgressBar()

    def __del__(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        # Related kv will be return
        super(BoxLayout, self).__init__(*args, **kwargs)

        if 'initialize' in kwargs:
            screen_button = {
                'Changes' : self.changes_button,
                'History' : self.history_button,
                'Branches' : self.branches_button,
                'Settings' : self.settings_button
            }

            # previously selected repo should be found.
            try:
                reponame = settings.DB.store_get('current_repo').strip()
                repos = settings.DB.store_get('repos')
                repo = filter(lambda x: x['name'].strip() == reponame, repos)[0]
                repo_path = repo['path']
            except:
                repo_path = ""

            # Previously selected button and related screen is taken
            screen = settings.DB.store_get('screen')
            if screen == "FileDiff":
                screen = "History"
            screen_button[screen].make_pressed()

            # Based on the screen base model will be taken
            related_box = getattr(self.screen_manager, screen.lower()).children[0].children[0]

            # Then related box'es processes will be called.
            # To know that the screen was loaded before all
            # related processes is called.
            function_name = ""
            for func in ['changes_check', 'branches_check',
                         'check_history', 'settings_check']:
                if hasattr(related_box, func):
                    function_name = func
                    break

            if function_name == 'changes_check':
                tasks = [self.show_kv(screen),
                         self.activate_sync(repo_path),
                         self.get_branches(repo_path),
                         related_box.get_userinfo(repo_path),
                         related_box.get_difffiles(repo_path),
                         related_box.get_unpushedcommits(repo_path),
                         related_box.get_current_branch(repo_path)]

            elif function_name == 'branches_check':
                tasks = [self.show_kv(screen),
                         self.activate_sync(repo_path),
                         self.get_branches(repo_path),
                         related_box.set_repopath(repo_path),
                         related_box.handle_merge_view(repo_path),
                         related_box.remove_newbranch_widget(repo_path),
                         related_box.remove_rename_widget(repo_path),
                         related_box.get_branches(repo_path),
                         related_box.clear_buttonactions(repo_path)]

            elif function_name == 'check_history':
                tasks = [self.show_kv(screen),
                         self.activate_sync(repo_path),
                         self.get_branches(repo_path),
                         related_box.get_history(repo_path),
                         related_box.get_diff_clear(repo_path)]

            elif function_name == 'settings_check':
                tasks = [self.show_kv(screen),
                         self.activate_sync(repo_path),
                         self.get_branches(repo_path),
                         related_box.set_repopath(repo_path),
                         related_box.get_remote(repo_path),
                         related_box.get_gitignore(repo_path)]

            # Processes will be called and displayed completed ones on animation.
            ProgressAnimator(self.pb, tasks)
            os.chdir(settings.PROJECT_PATH)


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

        settings.DB.store_put('screen', value)
        settings.DB.store_sync()

        def _wrapper(callback=None):
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
                repo_path = pressed_repo[0].repo_path if pressed_repo else ""

                # Related screen and repository data merged and screen datas update.
                if repo_path:
                    if selected_menu_class == ChangesBox().__class__:
                        child.children[0].changes_check(repo_path)

                    elif selected_menu_class == HistoryBox().__class__:
                        keep_old = False
                        if prev == 'FileDiff':
                            keep_old = True
                        child.children[0].check_history(repo_path,
                                                        keep_old = keep_old)

                    elif selected_menu_class == BranchesBox().__class__:
                        child.children[0].branches_check(repo_path)

                    elif selected_menu_class == SettingsBox().__class__:
                        child.children[0].settings_check(repo_path)
                else:
                    if selected_menu_class == BranchesBox().__class__:
                        child.children[0].remove_newbranch_widget("")
                        child.children[0].remove_rename_widget("")
                        child.children[0].handle_merge_view("")
            except (WidgetException, ScreenManagerException):
                pass

            if callback:
                callback()

        return _wrapper

    def activate_sync(self, path):
        def _wrapper(callback=None):
            if path:
                self.syncbutton.text = self.syncbutton.text.\
                                    replace(settings.HEX_COLOR1,'000000')
                self.syncbutton.path = path
            if callback:
                callback()
        return _wrapper

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


    def theme_args_converter(self, row_index, item):
        """
        theme_args_converter; is for converting only color schemas
        """
        return {
            'name': item
        }


    def args_converter(self, row_index, item):
        """
        args_converter, for displaying repositories
        To display a list of data this convertion style is
        requested for kivy Factory method.
        """
        return {
            'repo_path': item['path'],
            'repo_name': item['name'],
            'init_pressed': item['init_pressed']}

    def load_repo(self, reset=True):
        """
        load_repo, for loading repository list from .json file (if exists).
        file path is found on settings. In any exception repos sets to empty list
        """
        try:
            self.repos = settings.DB.store_get('repos')
            settings.DB.store_sync()
            try:
                reponame = settings.DB.store_get('current_repo').strip()
                repo = filter(lambda x: x['name'].strip() == reponame, self.repos)[0]
                for rep in self.repos:
                    rep['init_pressed'] = True if rep == repo else False
            except: pass
        except (TypeError, ValueError, KeyError):
            directory = os.path.dirname(settings.REPOFILE)
            if not os.path.exists(directory):
                os.makedirs(directory)
                settings.DB.store_put('repos', [])
                settings.DB.store_sync()
            self.repos = []
        if reset:
            self.reset_screen()

    def remove_repo(self, path):
        try:
            repos = settings.DB.store_get('repos')
            self.repos = filter(lambda x: x['path'] != path, repos)
            settings.DB.store_put('repos', self.repos)
            settings.DB.store_sync()
        except (TypeError, ValueError):
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

    def get_branches(self, path):
        """
        get_branches, collects local branches of repository

        ::path: Repository path.
        ::callback: at the end method calls

        callback method is for to show the progression of bulk of method if any.
        """
        def _wrapper(callback=None):
            if path:
                os.chdir(path)
                out = run_syscall('git branch')
                values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
                text = self.get_activebranch(path)
                self.branchlist.text = "[color=%s][b]%s[/b][/color]"%(settings.HEX_COLOR1, text)
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

        return _wrapper

    def change_branch(self, branch_name, path):
        """
        change_branch, handle changing current branches.

        ::branch_name: branch name which wanted to checkout
        ::path: related repository path

        branch name is marked up to use that markup should be cleared
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
    icon = ICON_PATH
    title = "Git Watcher UI"
    observer = Observer()

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
        Builder.load_file('%(pp)s%(ps)sassets%(ps)sthemes%(ps)sCompact.kv'%\
                                                    {'pp':settings.PROJECT_PATH,
                                                     'ps':settings.PATH_SEPERATOR})

        self.layout = RepoWatcher(initialize=True)
        self.layout.load_repo()

        return self.layout

        # Without border
        # Window.borderless = True

        # Position of mouse when the app starts
#         def mouse_pos(self, position):
#             def take_buttons(obj, buttons):
#                 """
#                 take_buttons, collect the button sets of current screen
#                 :obj:: kivy object.
#                 :buttons:: a list of buttons, before an empty array.
#                 """
#                 if hasattr(obj, 'on_release'):
#                     buttons.append(obj)
#                 for child in obj.children:
#                     take_buttons(child, buttons)
#                 return buttons
#
#             buttons = take_buttons(Window.children[0], [])
#             but = filter(lambda x: x.pos[0]< position[0] <x.pos[0]+x.width and \
#                                    x.pos[1]< position[1] <x.pos[1]+x.height ,
#                             buttons)
#
#             if but:
#                 print map(lambda x: (x.pos,x), but)
#
#         Window.bind(mouse_pos=mouse_pos)

    def restart(self):
        # TO-DO: Not yet implemented.
        pass

    def observer_start(self, repo_path):
        event_handler = self.MyHandler()
        self.observer.schedule(event_handler, path=repo_path, recursive=False)
        self.observer.start()

    def observer_stop(self):
        self.observer.stop()

    def on_stop(self):
        self.observer_stop()


if __name__ == '__main__':
    RepoWatcherApp().run()
