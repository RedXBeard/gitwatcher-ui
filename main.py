import os
import json
import settings
from subprocess import Popen, PIPE
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

class CommandLineException(Exception):
    pass


cmd = "echo $HOME"
p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()


def run_syscall(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if not out:
        raise CommandLineException
    return out.rstrip()

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


class MenuButton(Button):
    def on_press(self):
        if Builder.files[1] == "Default.kv":
            if self.state == "down":
                if self.uid != self.parent.addrepo.uid:
                    self.background_color = 1, 1, 1, 1
                buttons = [self.parent.history,
                           self.parent.changes,
                           self.parent.branches,
                           self.parent.settings,
                           self.parent.addrepo]
                for obj in buttons:
                    if obj.uid != self.uid:
                        obj.background_color = 2, 2, 2, 9
        else:
            if self.state == "down":
                if self.parent.repoadd_button and \
                        self.uid != self.parent.repoadd_button.uid:
                    self.background_color = 1, 1, 1, 1

                buttons = self.parent.parent.menu_list.children
                for but in buttons:
                    if but.uid != self.uid:
                        but.background_color = 2, 2, 2, 9
                    else:
                        but.background_color = 1, 1, 1, 1

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
                    data.append({"name": repo_name,
                                 "path": repo_path})
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


class RepoDetailButton(Button):
    def on_press(self):
        pressed = self.parent.parent.repobutton.children
        pressed_area = self.parent.parent
        unpressed_button_list = filter(lambda x: x != pressed_area,
                                       self.parent.parent.parent.children)
        for child in pressed:
            child.background_color = [.9, .9, 2, 1]

        for child in unpressed_button_list:
            for but in child.repobutton.children:
                but.background_color = [.7, .7, 1, 1]


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

    def args_converter(self, row_index, item):
        return {
            'repo_index': row_index,
            'repo_path': item['path'],
            'repo_name': item['name']}

    def history_args_converter(self, row_index, item):
        return {
            'branch_index': row_index,
            'branch_commiter': item['commiter'],
            'branch_message': item['message'],
            'branch_date': item['date'],
            'branch_logid': item['logid'],
            'branch_path': item['path']}

    def load_repo(self):
        try:
            repofile = file(REPOFILE, "r")
            self.repos = json.loads(repofile.read())
            repofile.close()
            self.history = []
        except (IOError, TypeError, ValueError):
            self.repos = []
            self.history = []

    def load_history(self, path):
        os.chdir(path)
        out = run_syscall('git log --pretty=format:"%h - %an , %ar : %s"')
        lines = out.split("\n")
        self.history = []
        for l in lines:
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
            self.history.append(tmp)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
        if Builder.files[1] == "Default.kv":
            self.menu.branchlist.text = text
            self.menu.branchlist.values = values
            self.menu.branchlist.path = path
            os.chdir(settings.PROJECT_PATH)
            self.menu.branchlist.font_name = settings.KIVY_DEFAULT_FONT
            self.repo.textarea.text = ""
            self.repo.textscroll.bar_pos_x = 'top'
        else:
            self.branchlist.text = text
            self.branchlist.values = values
            self.branchlist.path = path
            os.chdir(settings.PROJECT_PATH)
            self.branchlist.font_name = settings.KIVY_DEFAULT_FONT
            self.textscroll.textarea.text = ""
            self.textscroll.textarea.bar_pos_x = 'top'

    def load_diff(self, path, logid):
        os.chdir(path)
        try:
            out = run_syscall('git show %s' % logid)
        except CommandLineException:
            out = "Error Occured"
        out = diff_formatter(out)
        if Builder.files[1] == "Default.kv":
            self.repo.textarea.text = "[color=000000]%s[/color]" % out
            self.repo.textscroll.bar_pos_x = 'top'
        else:
            self.textscroll.textarea.text = "[color=000000]%s[/color]" % out
            self.textscroll.textarea.bar_pos_x = 'top'

    def change_branch(self, branch_name, path):
        try:
            os.chdir(path)
            out = run_syscall('git stash;git checkout %s' % branch_name)
            self.load_history(path)
        except OSError:
            pass


class RepoWatcherApp(App):
    def build(self):
        self.title = "Repo Watcher"

        Builder.load_file('Compact.kv')

        layout = RepoWatcher()
        layout.load_repo()
        return layout

    def load_repo(self):
        self.layout.load_repo()

    def load_history(self):
        self.layout.load_history()


if __name__ == '__main__':
    RepoWatcherApp().run()
