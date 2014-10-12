from kivy.app import App
from kivy.uix.widget import Widget, ObjectProperty
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


class RepoItem(BoxLayout):
    repo_name = StringProperty()
    repo_path = StringProperty()
    repo_index = NumericProperty()

class CustomButton(Button):
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

            # if self.uid == self.parent.addrepo.uid:
            #     content = Button(text='Close me!')
            #     popup = Popup(content=content,
            #                   title='Add Existing Repo',
            #                   size_hint=(None, None), size=(400, 400))
            #     content.bind(on_press=popup.dismiss)
            #     popup.open()

class RepoWatcher(GridLayout):
    data = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'repo_index': row_index,
            'repo_path': item['path'],
            'repo_name': item['name']}

class RepoWatcherApp(App):

    def build(self):
        self.title= "Repo Watcher"
        layout = RepoWatcher()
        layout.data = [{"path":"/Users/denizci/.virtualenvs/RomanAlphabet/project/RomanNumbers", "name":"RomanNumbers"},
                       {"path":"/Users/denizci/.virtualenvs/sqldict/project/python-sqldict","name":"sqldict"},
                       {"path":"/Users/denizci/.virtualenvs/django_maskurl/project/django_maskurl","name":"django-maskurl"}]
        #layout.add_repos()
        return layout

if __name__ == '__main__':
    RepoWatcherApp().run()
