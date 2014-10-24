from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

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

class DiffItem(BoxLayout):
    path = StringProperty()
    diff = StringProperty()
    repo_path = StringProperty()
