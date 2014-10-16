import os
import json
from subprocess import Popen, PIPE
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout


class CommandLineException(Exception):
    pass

cmd = "echo $HOME"
p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()


def run_syscall(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err:
        raise CommandLineException
    return out.rstrip()

def diff_formatter(text):
    green = "\n+"
    red = "\n-"
    location = 0

    text_set = []

    green_text = text
    red_text = text

    new_text = ""

    while location != -1:
        tmp_location = green_text.find(green)
        if tmp_location != -1:
            text = green_text[location:tmp_location]
            line_end = green_text[tmp_location+3:].find("\n")
            text += "\n[color=00ff00]+%s[/color]"%\
                    green_text[tmp_location+3:tmp_location+3+line_end+1]
            location = tmp_location+3+line_end+1
            green_text = green_text[location:]
        else:
            text += green_text
            location = -1

    return text



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


class AddRepoButton(Button):
    def on_press(self):
        if self.text == "Add Repo":
            selection = self.parent.parent.repopath.text
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
            except TypeError:
                data = []
            repofile.close()
            repofile = file(REPOFILE, "w")
            os.chdir(selection)
            if os.path.exists(".git"):
                out = run_syscall("basename `git rev-parse --show-toplevel`")
                repo_name = out
                repo_path = selection
                data.append({"name": repo_name,
                             "path": repo_path})
                json_result = json.dumps(data)
                repofile.write(json_result)
            repofile.close()


class RepoDetailButton(Button):
    def on_press(self):
        pressed = self.parent.parent.repobutton.children
        pressed_area = self.parent.parent
        unpressed_button_list = filter(lambda x: x != pressed_area,
                                    self.parent.parent.parent.children)
        for child in pressed:
            child.background_color = [0,0,0,1]

        for child in unpressed_button_list:
            for but in child.repobutton.children:
                but.background_color = [1,1,1,1]

        self.parent.parent.parent.parent.parent.parent.\
                parent.parent.load_history(self.repo_path)

class HistoryButton(Button):
    def on_press(self):
        self.background_color = [0,0,0,1]

        for child in self.parent.parent.parent.children:
            for box in child.children:
                for it in box.children:
                    if it.__class__ == self.__class__ and \
                        it.uid != self.uid:
                        it.background_color = [1,1,1,1]

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
        except (IOError, TypeError):
            self.repos = []

    def load_history(self, path):
        os.chdir(path)
        out = run_syscall('git log --pretty=format:"%h - %an , %ar : %s"')
        lines = out.split("\n")
        self.history = []
        for l in lines:
            tmp = dict(commiter="", message="", date="", logid="", path=path)
            tmp["logid"] = l.split(" - ")[0].strip();
            l = l.split(" - ")[1:][0].strip()
            tmp["commiter"] = l.split(" , ")[0].strip();
            l = l.split(" , ")[1:][0].strip()
            tmp["date"] = l.split(" : ")[0].strip();
            l = l.split(" : ")[1:][0].strip()
            if len(l) > 50:
                l = "%s..." % l[:50]
            tmp["message"] = l
            self.history.append(tmp)
        self.repo.textarea.text = ""

    def load_diff(self, path, logid):
        os.chdir(path)
        try:
            out = run_syscall('git show %s' % logid)
        except CommandLineException:
            out = "Error Occured"
        out = diff_formatter(out)
        self.repo.textarea.text = "[color=000000]%s[/color]"%out


class RepoWatcherApp(App):
    def build(self):
        self.title = "Repo Watcher"

        # TODO: Checking out for Windows
        try:
            system = run_syscall("uname")
            if system == "Linux":
                Builder.load_file('RepoWatcher.kv')
        except CommandLineException:
            pass

        layout = RepoWatcher()
        layout.load_repo()
        return layout

    def load_repo(self):
        self.layout.load_repo()

    def load_history(self):
        self.layout.load_history()


if __name__ == '__main__':
    RepoWatcherApp().run()
