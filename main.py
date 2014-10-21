import os
import json
import re
import settings
from subprocess import Popen, PIPE
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ListProperty, StringProperty, DictProperty, \
                            NumericProperty, ObjectProperty
from kivy.lang import Builder, Parser, ParserException
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar


cmd = "echo $HOME"
p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()

KVS = os.path.join(settings.PROJECT_PATH, "assets/themes")
CLASSES = [c[:-3] for c in os.listdir(KVS) if c.endswith('Menu.kv') ]
ICON_PATH = os.path.join(settings.PROJECT_PATH, 'assets/icon') + 'gitwatcher-ui_icon.png'

class CommandLineException(Exception):
    pass


def run_syscall(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()

def striptags(text):
    return re.sub(r'\[[^>]*?\]', '', text)

def create_popup(title, content):
    popup = Popup(title=title, content=content,
                  size_hint=(None, None), size=(300, 100))
    return popup

def diff_formatter(text):
    def replacer(text, search, color):
        result_text = ""
        location = 0

        while location != -1:
            tmp_location = text.find(search)
            if tmp_location != -1:
                result_text += text[:tmp_location]
                line_end = text[tmp_location + 2:].find("\n")
                if line_end > 0:
                    result_text += "\n[color=%s]%s[/color]" % \
                                   (color,
                                    text[tmp_location + 1:tmp_location + 2 + line_end])
                else:
                    result_text += "\n[color=%s]%s[/color]" % \
                                   (color, text[tmp_location + 1:])
                    text = ""
                location = tmp_location + 2 + line_end
                text = text[location:]
            else:
                result_text += text
                location = -1
        return result_text

    green = "\n+"
    red = "\n-"
    tmp_text = text

    return replacer(replacer(tmp_text, green, "00ff00"), red, "ff0000")


class Menu(BoxLayout):

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        parser = Parser(content=open(self.kv_file).read())
        widget = Factory.get(parser.root.name)()
        Builder._apply_rule(widget, parser.root, parser.root)
        self.add_widget(widget)

    @property
    def kv_file(self):
        '''HistoryMenu'''
        return os.path.join(KVS, self.__class__.__name__ + '.kv')

for class_name in CLASSES:
    globals()[class_name] = type(class_name, (Menu,), {})

class RepoItem(BoxLayout):
    repo_name = StringProperty()
    repo_path = StringProperty()
    repo_index = NumericProperty()


class RepoHistoryItem(BoxLayout):
    branch_commiter = StringProperty()
    branch_message = StringProperty()
    branch_date = StringProperty()
    branch_logid = StringProperty()
    branch_path = StringProperty()
    branch_index = NumericProperty()
    diff_files = ListProperty()


class ChangesItem(BoxLayout):
    file_name = StringProperty()
    repo_path = StringProperty()


class UnPushedItem(BoxLayout):
    sha = StringProperty()
    subject = StringProperty()
    path = StringProperty()


class BranchesItem(BoxLayout):
    date = StringProperty()
    sha = StringProperty()
    name = StringProperty()
    commiter = StringProperty()
    subject = StringProperty()


class MenuButton(Button):
    def on_press(self):
        if Builder.files[1] == "assets/themes/Default.kv":
            if self.state == "down":
                if self.uid != self.parent.addrepo.uid:
                    self.background_color = 1, 1, 2.5, 1
                    self.pressed = True

                buttons = [self.parent.history,
                           self.parent.changes,
                           self.parent.branches,
                           self.parent.settings,
                           self.parent.addrepo]
                for obj in buttons:
                    if obj.uid != self.uid:
                        obj.background_color = 1, 1, 1.5, 0.5
                        self.pressed = False
        else:
            root = self.parent.parent.parent.parent
            if self.state == "down":
                if self.parent.repoadd_button and \
                        self.uid != self.parent.repoadd_button.uid:
                    self.background_color = 1, 1, 2.5, 1
                    self.pressed = False

                buttons = self.parent.parent.menu_list.children
                for but in buttons:
                    if but.uid != self.uid:
                        but.background_color = 1, 1, 1.5, 0.5
                        but.pressed = False
                    else:
                        but.background_color = 1, 1, 2.5, 1
                        but.pressed = True

    def on_release(self):
        root = self.parent.parent.parent.parent
        repos = filter(lambda x: x.repobutton.children[0].pressed,
                            root.repolstview.children[0].children[0].children)


class AddRepoButton(Button):
    def on_press(self):
        selection = None
        popup = None
        if self.text == "Add Repo":
            selection = self.parent.parent.repoaddbox.repopath.text
            self.parent.parent.popup.dismiss()
        elif self.text == "Choose" and self.parent.listview.selection:
            selection = self.parent.listview.selection[0]
        if selection:
            directory = os.path.dirname(REPOFILE)
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                repofile = file(REPOFILE, "r")
            except IOError:
                repofile = file(REPOFILE, "w")
            try:
                data = json.loads(repofile.read())
            except (IOError, TypeError, ValueError):
                data = []
            repofile.close()
            if os.path.exists(selection):
                os.chdir(selection)
                if os.path.exists(".git"):
                    repofile = file(REPOFILE, "w")
                    out = run_syscall("basename `git rev-parse --show-toplevel`")
                    repo_name = out
                    repo_path = selection
                    if not filter(lambda x: x["name"] == repo_name and \
                                            x["path"] == repo_path,
                                  data):
                        data.append({"name": repo_name,
                                     "path": repo_path})
                    else:
                        popup = create_popup('Already Listed', Label(text=''))
                    json_result = json.dumps(data)
                    repofile.write(json_result)
                else:
                    popup = create_popup('Error', Label(text='Invalid repo path'))
            else:
                popup = create_popup('Error', Label(text='Invalid repo path'))

            repofile.close()
        else:
            popup = create_popup('Error', Label(text='Invalid repo path'))
        if popup:
            popup.open()
        os.chdir(settings.PROJECT_PATH)


class RepoDetailButton(Button):
    def on_press(self):
        pressed = self.parent.parent.repobutton.children
        pressed_area = self.parent.parent
        unpressed_button_list = filter(lambda x: x != pressed_area,
                                       self.parent.parent.parent.children)
        for child in pressed:
            child.background_color = [.9, .9, 2, 1]
            child.pressed = True

        for child in unpressed_button_list:
            for but in child.repobutton.children:
                but.background_color = [.7, .7, 1, 1]
                but.pressed = False

    def on_release(self):
        root = self.parent.parent.parent.parent.parent.parent.parent.parent
        screen = root.screen_manager.children[0].children[0].children[0]
        if root.history_button.pressed:
            root.load_history(self.repo_path)

        elif root.changes_button.pressed:
            os.chdir(self.repo_path)
            out = run_syscall('git branch')
            values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
            text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")

            root.branchlist.text = "[b]%s[/b]"%text
            root.branchlist.values = values
            root.branchlist.path = self.repo_path
            root.branchlist.font_name = settings.KIVY_DEFAULT_FONT
            screen.info.text = screen.info.text.split(" ")[0] + \
                               "[color=575757][size=12] Committing to %s[/size][/color]"%text

            screen.changes_check(self.repo_path)

        elif root.branches_button.pressed:
            os.chdir(self.repo_path)
            out = run_syscall('git branch')
            values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
            text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
            root.branchlist.text = "[b]%s[/b]"%text
            root.branchlist.values = values
            root.branchlist.path = self.repo_path
            root.branchlist.font_name = settings.KIVY_DEFAULT_FONT

            os.chdir(self.repo_path)
            script = "git for-each-ref --format='%(committerdate:short)"
            script += " ; %(authorname) , %(refname:short),%(objectname:short)"
            script += " : %(subject)' --sort=committerdate refs/heads/"
            out = run_syscall(script).strip()
            screen.branches = []
            for l in out.split("\n"):
                tmp = dict(date="", name="", sha="", commiter="", subject="")
                tmp['subject'] = l.split(':')[-1]; l = l.split(':')[0].strip()
                tmp['sha'] = l.split(',')[-1]; l = ','.join(l.split(',')[:-1])
                tmp['name'] = l.split(',')[-1]; l = l.split(',')[0].strip()
                tmp['commiter'] = l.split(';')[-1]; l = l.split(';')[0].strip()
                tmp['date'] = l
                if text and text == tmp['name'].strip():
                    screen.name = tmp['name'].strip()
                    screen.subject = tmp['subject'].strip()
                    screen.sha = tmp['sha'].strip()
                    screen.commiter = tmp['commiter'].strip()
                    screen.date = tmp['date'].strip()
                screen.branches.append(tmp)
        elif root.settings_button.pressed:
            os.chdir(self.repo_path)
            out = run_syscall('git branch')
            values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
            text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
            root.branchlist.text = "[b]%s[/b]"%text
            root.branchlist.values = values
            root.branchlist.path = self.repo_path
            root.branchlist.font_name = settings.KIVY_DEFAULT_FONT

            os.chdir(self.repo_path)
            try:
                gitignore = run_syscall('cat .gitignore')
                screen.gitignore.text = gitignore
            except CommandLineException:
                screen.gitignore.text = ""

            os.chdir(self.repo_path)
            out = run_syscall('git remote -v')
            try:
                origin = 'origin'.join(filter(lambda x: x.startswith('origin'), out.split("\n"))[0].split('origin')[1:]).strip()
                origin = ')'.join(origin.split("(")[:-1])
                screen.remote_path.text = origin
            except IndexError:
                screen.remote_path.text = ""
        else:
            pass
        os.chdir(settings.PROJECT_PATH)


class ChangesDiffButton(Button):
    def on_press(self):
        os.chdir(self.repo_path)
        out = diff_formatter(run_syscall('git diff %s'%self.file_name))
        screen = self.parent.parent.parent.parent.parent.parent.parent.parent
        screen.localdiff.localdiffarea.text = "[color=000000]%s[/color]"%out
        os.chdir(settings.PROJECT_PATH)


class CommitButton(Button):
    def on_press(self):
        also_push = self.parent.commitpushbutton.state == 'down'
        description = self.parent.parent.message.text
        commits = self.parent.parent.uncommitted.children[0].children[0].children
        if not commits:
            popup = create_popup('Commiting...', Label(text='There is nothing to commit.'))
            popup.open()
        elif not description:
            popup = create_popup('Commiting...', Label(text='Commit message is required.'))
            popup.open()
        else:
            commit_paths = []
            repopath = ""
            for c in commits:
                checkbox = c.children[0].checkbox
                filepath = "%s/%s"%(c.children[0].filename.repo_path,
                                    c.children[0].filename.file_name)
                repopath = c.children[0].filename.repo_path
                if checkbox.active:
                    commit_paths.append(filepath)
            if commit_paths:
                os.chdir(repopath)
                out = run_syscall('git add %s'% ' '.join(commit_paths))
                os.chdir(repopath)
                out = run_syscall('git commit -m "%s"'% description)
                if also_push:
                    branchname = striptags(self.parent.parent.parent.parent.\
                                    parent.parent.parent.parent.branchlist.text)

                    os.chdir(repopath)
                    out = run_syscall('git push origin %s' % branchname)
            self.parent.parent.parent.parent.changes_check(repopath)


class CommitandPushButton(ToggleButton):
    def on_press(self):
        if self.state == 'down':
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit", "Commit & Push")
            self.parent.commitbutton.width = '126dp'
        else:
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit & Push", "Commit")
            self.parent.commitbutton.width = '80dp'

    pass


class UnPushedButton(Button):
    pass


class SettingsButton(Button):
    pass


class BranchesBox(BoxLayout):
    name = StringProperty()
    subject = StringProperty()
    sha = StringProperty()
    commiter = StringProperty()
    date = StringProperty()
    branches = ListProperty()

    def __init__(self, *args, **kwargs):
        super(BranchesBox, self).__init__(*args, **kwargs)
        self.name = ""
        self.subject = ""
        self.sha = ""
        self.commiter = "Repo selection needed"

    # git for-each-ref --format='%(committerdate:short) - %(authorname) , %(refname:short),%(objectname:short) : %(subject)' --sort=committerdate refs/heads/ --python
    def args_converter(self, row_index, item):
        return {
            'index': row_index,
            'date': item['date'],
            'sha': item['sha'],
            'name': item['name'],
            'commiter': item['commiter'],
            'subject': item['subject']
        }

class ChangesBox(BoxLayout):
    changes = ListProperty()
    unpushed = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'index': row_index,
            'file_name': item['name'],
            'repo_path': item['path']}

    def unpushed_args_converter(self, row_index, item):
        return {
            'index': row_index,
            'sha': item['sha'],
            'subject': item['subject'],
            'path': item['path']}

    def changes_check(self, path):
        os.chdir(path)
        self.message.text = ""
        name = run_syscall('git config --global user.name')
        email = run_syscall('git config --global user.email')
        text = "[color=000000][size=12]%s[/size]\n"
        text += "[size=9]%s[/size]\n"
        text += "[size=13][b]Uncommitted Changes[/b][/size][/color]"
        text = text%(name, email)
        self.userinfo.text = text

        os.chdir(path)
        files = run_syscall('git diff --name-only')
        self.localdiff.localdiffarea.text = ""
        self.changes = []
        if files:
            for f in files.split("\n"):
                tmp = dict(name=f, path=path)
                self.changes.append(tmp)
        path_value = self.repopathlabel.text
        path_value.split(" ")[0]
        repo_path_text = "[color=202020][size=10]%s[/size][/color]" % path
        repo_path_text = repo_path_text.replace(run_syscall(cmd), "~")
        self.repopathlabel.text = repo_path_text

        os.chdir(path)
        out = run_syscall('git log origin/master..HEAD --pretty="%h - %s"')
        self.unpushed = []
        self.unpushedlabel.text = ""
        if out:
            for l in out.split("\n"):
                tmp = dict(subject="", sha="", path=path)
                tmp['subject'] = " - ".join(l.split(" - ")[1:]).strip()
                tmp['sha'] = l.split(" - ")[0].strip()
                self.unpushed.append(tmp)
            self.unpushedlabel.text = "[color=000000][b]Unpushed Commits[/b][/color]"
        os.chdir(settings.PROJECT_PATH)


class HistoryBox(BoxLayout):
    history = ListProperty()

    def history_args_converter(self, row_index, item):
        return {
            'branch_index': row_index,
            'branch_commiter': item['commiter'],
            'branch_message': item['message'],
            'branch_date': item['date'],
            'branch_logid': item['logid'],
            'branch_path': item['path'],
            'diff_files': item['files']}

    def load_diff(self, path, logid):
        os.chdir(path)
        try:
            out = run_syscall('git show %s' % logid)
        except CommandLineException:
            out = "Error Occured"
        out = diff_formatter(out)
        if Builder.files[1] == "assets/themes/Default.kv":
            self.repo.textarea.text = "[color=000000]%s[/color]" % out
            self.repo.textscroll.bar_pos_x = 'top'
        else:
            self.textscroll.textarea.text = "[color=000000]%s[/color]" % out
            self.textscroll.textarea.bar_pos_x = 'top'
        os.chdir(settings.PROJECT_PATH)


class HistoryButton(Button):
    def on_press(self):
        self.background_color = [.9, .9, 2, 1]

        for child in self.parent.parent.parent.children:
            for box in child.children:
                for it in box.children:
                    if it.__class__ == self.__class__ and \
                        it.uid != self.uid:
                        it.background_color = [.7, .7, 1, 1]


class RepoWatcher(GridLayout):
    repos = ListProperty()
    history = ListProperty()
    active_menu_button = StringProperty()
    screen_manager = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(GridLayout, self).__init__(*args, **kwargs)
        self.active_menu_button = "changes"
        self.show_kv('Changes')

    def show_kv(self, value):
        self.screen_manager.current = value
        child = self.screen_manager.current_screen.children[0]

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

    def load_history(self, path):
        os.chdir(path)
        out = run_syscall('git log --pretty=format:"%h - %an , %ar : %s |||" --name-only')
        lines = out.split("\n\n")
        self.history = []
        for group in lines:
            group = group.split("|||")
            files = group[-1]
            l = "|||".join(group[:-1])
            files = files.strip().split("\n")
            tmp = dict(commiter="", message="", date="", logid="", path=path)
            tmp["logid"] = l.split(" - ")[0].strip()
            l = l.split(" - ")[1:][0].strip()
            tmp["commiter"] = l.split(" , ")[0].strip()
            l = l.split(" , ")[1:][0].strip()
            tmp["date"] = l.split(" : ")[0].strip()
            l = l.split(" : ")[1:][0].strip()
            if len(l) > 50:
                l = "%s..." % l[:50]
            tmp["message"] = l
            tmp["files"] = files
            self.history.append(tmp)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
        if Builder.files[1] == "assets/themes/Default.kv":
            self.menu.branchlist.text = text
            self.menu.branchlist.values = values
            self.menu.branchlist.path = path
            os.chdir(settings.PROJECT_PATH)
            self.menu.branchlist.font_name = settings.KIVY_DEFAULT_FONT
            self.repo.textarea.text = ""
            self.repo.textscroll.bar_pos_x = 'top'
        else:
            plural='s' if len(self.history) > 1 else ''
            screen = self.screen_manager.children[0].children[0].children[0]
            if self.screen_manager.current == "History":
                screen.repohistory_count.text = "[color=000000][size=12][b]%s commit%s[/b][/size][/color]"%\
                                                    (len(self.history), plural)
                screen.textscroll.textarea.text = ""
                screen.textscroll.textarea.bar_pos_x = 'top'
                screen.history = self.history

            self.branchlist.text = "[b]%s[/b]"%text
            self.branchlist.values = values
            self.branchlist.path = path
            os.chdir(settings.PROJECT_PATH)
            self.branchlist.font_name = settings.KIVY_DEFAULT_FONT

    def change_branch(self, branch_name, path):
        try:
            os.chdir(path)
            out = run_syscall('git stash;git checkout %s' % branch_name)
            screen = self.screen_manager.children[0].children[0].children[0]
            if self.screen_manager.current == "History":
                self.load_history(path)
            elif self.screen_manager.current == "Changes":
                os.chdir(path)
                out = run_syscall('git branch')
                values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
                text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
                self.branchlist.text = "[b]%s[/b]"%text
                self.branchlist.values = values
                self.branchlist.path = path
                os.chdir(settings.PROJECT_PATH)
                self.branchlist.font_name = settings.KIVY_DEFAULT_FONT
                screen.info.text = screen.info.text.split(" ")[0] + \
                                   "[color=575757][size=12] Committing to %s[/size][/color]"%text
            elif self.screen_manager.current == "Branches":
                os.chdir(path)
                out = run_syscall('git branch')
                values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
                text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
                self.branchlist.text = "[b]%s[/b]"%text
                self.branchlist.values = values
                self.branchlist.path = path
                self.branchlist.font_name = settings.KIVY_DEFAULT_FONT

                os.chdir(path)
                script = "git for-each-ref --format='%(committerdate:short)"
                script += " ; %(authorname) , %(refname:short),%(objectname:short)"
                script += " : %(subject)' --sort=committerdate refs/heads/"
                out = run_syscall(script).strip()
                screen.branches = []
                for l in out.split("\n"):
                    tmp = dict(date="", name="", sha="", commiter="", subject="")
                    tmp['subject'] = l.split(':')[-1]; l = l.split(':')[0].strip()
                    tmp['sha'] = l.split(',')[-1]; l = ','.join(l.split(',')[:-1])
                    tmp['name'] = l.split(',')[-1]; l = l.split(',')[0].strip()
                    tmp['commiter'] = l.split(';')[-1]; l = l.split(';')[0].strip()
                    tmp['date'] = l
                    if text and text == tmp['name'].strip():
                        screen.name = tmp['name'].strip()
                        screen.subject = tmp['subject'].strip()
                        screen.sha = tmp['sha'].strip()
                        screen.commiter = tmp['commiter'].strip()
                        screen.date = tmp['date'].strip()
                    screen.branches.append(tmp)
            elif self.screen_manager.current == 'Settings':
                os.chdir(path)
                out = run_syscall('git branch')
                values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
                text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
                self.branchlist.text = "[b]%s[/b]"%text
                self.branchlist.values = values
                self.branchlist.path = path
                self.branchlist.font_name = settings.KIVY_DEFAULT_FONT

                os.chdir(path)
                try:
                    gitignore = run_syscall('cat .gitignore')
                    screen.gitignore.text = gitignore
                except CommandLineException:
                    screen.gitignore.text = ""

                os.chdir(path)
                out = run_syscall('git remote -v')
                try:
                    origin = 'origin'.join(filter(lambda x: x.startswith('origin'), out.split("\n"))[0].split('origin')[1:]).strip()
                    origin = ')'.join(origin.split("(")[:-1])
                    screen.remote_path.text = origin
                except IndexError:
                    screen.remote_path.text = ""
        except OSError:
            pass
        finally:
            os.chdir(settings.PROJECT_PATH)


class RepoWatcherApp(App):
    pb = None
    popup = None
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
