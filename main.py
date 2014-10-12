import os, json
from subprocess import Popen, PIPE
from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

# basename `git rev-parse --show-toplevel`
REPOFILE = "~/.kivyrepowatcher/repowatcher"

class RepoItem(BoxLayout):
    repo_name = StringProperty()
    repo_path = StringProperty()
    repo_index = NumericProperty()

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
            self.parent.parent.repopath.text
            self.parent.parent.popup.dismiss()
        elif self.text == "Choose" and self.parent.listview.selection:
            selection = self.parent.listview.selection[0]
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
                cmd = "basename `git rev-parse --show-toplevel`"
                p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                repo_name = out.rstrip()
                repo_path = selection
                data.append({"name": repo_name,
                             "path": repo_path})
                json_result = json.dumps(data)
                repofile.write(json_result)
            repofile.close()

class RepoWatcher(GridLayout):
    data = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'repo_index': row_index,
            'repo_path': item['path'],
            'repo_name': item['name']}

    def load_data(self):
        try:
            repofile = file(REPOFILE, "r")
            self.data = json.loads(repofile.read())
        except: self.data=[]

class RepoWatcherApp(App):

    def build(self):
        self.title= "Repo Watcher"
        layout = RepoWatcher()
        layout.load_data()
        return layout

    def load_data(self):
        self.layout.load_data()

if __name__ == '__main__':
    RepoWatcherApp().run()
