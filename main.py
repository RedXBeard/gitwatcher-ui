import os, json
from subprocess import Popen, PIPE
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget, ObjectProperty
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

cmd = "echo $HOME"
p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
REPOFILE = "%s/.kivyrepowatcher/repowatcher"%out.rstrip()

def run_syscall(cmd):
    p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()

class RepoItem(BoxLayout):
    repo_name = StringProperty()
    repo_path = StringProperty()
    repo_index = NumericProperty()


class RepoHistoryItem(BoxLayout):
    branch_commiter =  StringProperty()
    branch_message = StringProperty()
    branch_date = StringProperty()
    branch_logid = StringProperty()
    branch_path = StringProperty()
    branch_index = NumericProperty()

class MenuButton(Button):
    def on_press(self):
        if self.state == "down":
            if self.uid != self.parent.addrepo.uid:
                self.background_color = 1,1,1,1
            buttons = [self.parent.history,
                       self.parent.changes,
                       self.parent.branches,
                       self.parent.settings,
                       self.parent.addrepo]
            for obj in buttons:
                if obj.uid != self.uid:
                    obj.background_color = 2,2,2,9

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
            except:
                repofile = file(REPOFILE, "w")
            try:
                data = json.loads(repofile.read())
            except: data=[]
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
        print "%s button pressed"%self.repo_path


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
        except: self.data=[]


    def load_history(self, path):
        os.chdir(path)
        out = run_syscall('git log --pretty=format:"%h - %an , %ar : %s"')
        lines = out.split("\n")
        self.history = []
        for l in lines:
            tmp = {"commiter":"", "message":"","date":"","logid":"","path":path}
            tmp["logid"] = l.split(" - ")[0].strip(); l=l.split(" - ")[1:][0].strip()
            tmp["commiter"] = l.split(" , ")[0].strip(); l=l.split(" , ")[1:][0].strip()
            tmp["date"] = l.split(" : ")[0].strip(); l=l.split(" : ")[1:][0].strip()
            if len(l) > 50:
                l = "%s..."%l[:50]
            tmp["message"] = l
            self.history.append(tmp)

    def load_diff(self, path, logid):
        os.chdir(path)
        try:
            out = run_syscall('git show %s'%logid)
        except: out = "Error Occured"
        self.repo.textarea.text = out


class RepoWatcherApp(App):

    def build(self):
        self.title= "Repo Watcher"
        Builder.load_file('RepoWatcher.kv')
        layout = RepoWatcher()
        layout.load_repo()
        return layout

    def load_repo(self):
        self.layout.load_repo()

    def load_history(self):
        self.layout.load_history()

if __name__ == '__main__':
    RepoWatcherApp().run()
