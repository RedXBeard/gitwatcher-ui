from kivy.properties import ListProperty, StringProperty, \
                            NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import AccordionItem

class RepoItem(BoxLayout):
    """
    RepoItem; on repository list,
        each element is using this class to display.
    """
    repo_name = StringProperty("")
    repo_path = StringProperty("")
    init_pressed = BooleanProperty(False)

    def __del__(self, *args, **kwargs):
        pass


class RepoHistoryItem(BoxLayout):
    """
    RepoHistoryItem; on history screen, on log list,
        each element is using this class to display.
    """
    branch_commiter = StringProperty("")
    branch_message = StringProperty("")
    branch_date = StringProperty("")
    branch_logid = StringProperty("")
    branch_path = StringProperty("")
    diff_files = ListProperty([])

    def __del__(self, *args, **kwargs):
        pass


class ChangesItem(BoxLayout):
    """
    ChangesItem; on changes screen, on ready to commit file list,
        each element is using this class to display.
    """
    file_name = StringProperty("")
    repo_path = StringProperty("")

    def __del__(self, *args, **kwargs):
        pass


class UnPushedItem(BoxLayout):
    """
    UnPushedItem: on changes screen, on already commited but not pushed list,
        each element is using this class to display.
    """
    sha = StringProperty("")
    subject = StringProperty("")
    path = StringProperty("")

    def __del__(self, *args, **kwargs):
        pass


class BranchesItem(BoxLayout):
    """
    BranchesItem; on branches screen, on other branches list,
        each element is using this class to display.
    """
    date = StringProperty("")
    sha = StringProperty("")
    name = StringProperty("")
    commiter = StringProperty("")
    subject = StringProperty("")
    published = BooleanProperty(False)
    merge = BooleanProperty(False)

    def __del__(self, *args, **kwargs):
        pass


class DiffItem(AccordionItem):
    """
    DiffItem; on history screen, selected log items, changed files list,
        each element is using this class to display.
    """
    path = StringProperty("")
    diff = StringProperty("")
    repo_path = StringProperty("")

    def __del__(self, *args, **kwargs):
        pass

class RemoteItem(BoxLayout):
    """
    RemoteItem; on push button pressed remote list should be displayed
        by this way, user can choose which remote will be
        used on pushing process
    """
    remote_path = StringProperty("")
    remote_name = StringProperty("")

    def __del__(self, *args, **kwargs):
        pass