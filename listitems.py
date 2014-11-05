from kivy.properties import ListProperty, StringProperty, \
                            NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

class RepoItem(BoxLayout):
    """
    RepoItem; on repository list,
        each element is using this class to display.
    """
    repo_name = StringProperty()
    repo_path = StringProperty()


class RepoHistoryItem(BoxLayout):
    """
    RepoHistoryItem; on history screen, on log list,
        each element is using this class to display.
    """
    branch_commiter = StringProperty()
    branch_message = StringProperty()
    branch_date = StringProperty()
    branch_logid = StringProperty()
    branch_path = StringProperty()
    branch_index = NumericProperty()
    diff_files = ListProperty()


class ChangesItem(BoxLayout):
    """
    ChangesItem; on changes screen, on ready to commit file list,
        each element is using this class to display.
    """
    file_name = StringProperty()
    repo_path = StringProperty()


class UnPushedItem(BoxLayout):
    """
    UnPushedItem: on changes screen, on already commited but not pushed list,
        each element is using this class to display.
    """
    sha = StringProperty()
    subject = StringProperty()
    path = StringProperty()


class BranchesItem(BoxLayout):
    """
    BranchesItem; on branches screen, on other branches list,
        each element is using this class to display.
    """
    date = StringProperty()
    sha = StringProperty()
    name = StringProperty()
    commiter = StringProperty()
    subject = StringProperty()

class DiffItem(BoxLayout):
    """
    DiffItem; on history screen, selected log items, changed files list,
        each element is using this class to display.
    """
    path = StringProperty()
    diff = StringProperty()
    repo_path = StringProperty()
