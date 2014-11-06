import os
import settings
import json
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.bubble import BubbleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

from listitems import ChangesItem, RepoHistoryItem, BranchesItem
from boxlayouts import HistoryBox, SettingsBox, ChangesBox, BranchesBox
from main import RepoWatcher, ConfirmPopup
from bubbles import NewSwitchRename
from shortcuts import create_popup, run_syscall, diff_formatter, \
                      striptags, findparent


class CustomTextInput(TextInput):
    def on_text_validate(self):
        branches = findparent(self, BranchesBox)
        path = branches.repo_path
        if path:
            os.chdir(path)
            out = run_syscall('git checkout -b %s'%self.text.strip())
            branches.branches_check(path)
        else:
            pass


class CustomBubbleButton(BubbleButton):
    def __init__(self, *args, **kwargs):
        super(CustomBubbleButton, self).__init__(*args, **kwargs)
        self.bind(on_press=self.on_press)

    def on_press(self, *args):
        pass

    def on_release(self, *args):
        root = findparent(self, BranchesBox)
        if self.text == "Switch to..":
            try:
                branch = findparent(self, BranchesItem)
                branch_name = striptags(branch.repobranchlabel.text).strip()
                os.chdir(root.repo_path)
                out = run_syscall("git checkout %s"%branch_name)
                root.branches_check(root.repo_path)
            except IndexError:
                popup = create_popup('Error Occured', Label(text=''))
                popup.open()
            finally:
                root.rename = False
                root.newbranch = False
                os.chdir(settings.PROJECT_PATH)
        elif self.text == "Rename":
            root.rename = not root.rename
            root.newbranch = False
            root.branches_check(root.repo_path)
        else:
            root.rename = False
            root.newbranch = not root.newbranch
            root.branches_check(root.repo_path)


class BranchMenuButton(ToggleButton):

    def __init__(self, *args, **kwargs):
        super(BranchMenuButton, self).__init__(*args, **kwargs)
        self.bind(on_release=self.show_bubble)

    def remove_bubbles(self):
        """
        remove_bubbles for remove already activated bubble widgets
        """
        root = findparent(self, BranchesBox)
        listed_buttons = set([root.branchmenubutton])
        for branchitem in root.branchlist.children[0].children[0].children:
            if str(branchitem.__class__).\
                        split('.')[1].replace('\'>','') == 'BranchesItem':
                listed_buttons.add(branchitem.children[1].children[0])
        for bi in listed_buttons:
            if bi != self and hasattr(bi, 'bubble'):
                bi.remove_widget(bi.bubble)
                delattr(bi, 'bubble')
                bi.state = 'normal'

    def show_bubble(self, *l):
        if not hasattr(self, 'bubble'):
            item = findparent(self, BranchesItem)
            newbranch_d = rename_d = switch_d = False
            if item:
                newbranch_d = rename_d = True
            else:
                switch_d = True

            self.bubble = bubble = NewSwitchRename(
                                        newbranch_disabled=newbranch_d,
                                        switch_disabled=switch_d,
                                        rename_disabled=rename_d)
            bubble.x = self.x - 250
            bubble.y = self.y
            self.add_widget(bubble)
            self.remove_bubbles()
        else:
            self.remove_widget(self.bubble)
            delattr(self, 'bubble')
            self.state = 'normal'
#             values = ('left_top', 'left_mid', 'left_bottom', 'top_left',
#                 'top_mid', 'top_right', 'right_top', 'right_mid',
#                 'right_bottom', 'bottom_left', 'bottom_mid', 'bottom_right')
#             index = values.index(self.bubb.arrow_pos)
#             self.bubb.arrow_pos = values[(index + 1) % len(values)]



class HistoryButton(Button):
    """
    HistoryButton; to manage user input on history screen, the button
        is used on list items of repository logs one box of log data
        contains at least four button.
    """
    def on_press(self):
        """
        on_press; default function name, for button classes on kivy.
            The press action trigger changing color of buttons in selected box.
        """
        root = findparent(self, RepoHistoryItem)

        for l in root.parent.children:
            if hasattr(l, 'pressed') and l.pressed:
                l.pressed = False

        button1 = root.button1
        button2 = root.button2
        button3 = root.button3
        button4 = root.button4
        button1.text = button1.text.replace('=777777', '=000000')
        button2.text = button2.text.replace('=777777', '=000000')
        button3.text = button3.text.replace('=777777', '=000000')
        button4.text = button4.text.replace('=777777', '=000000')
        root.pressed = True

        for l in root.parent.children:
            if hasattr(l, 'button1'):
                buttons = [l.button1, l.button2, l.button3, l.button4]
                if hasattr(l, 'pressed') and l.pressed:
                    for b in buttons:
                        b.text = b.text.replace('=777777', '=000000')
                else:
                    for b in buttons:
                        b.text = b.text.replace('=000000','=777777')

    def on_release(self):
        """
        on_release; another default function, which used to handle actual action.
            diff screen update operation is triggered with this buttons' release actions.
        """
        sub_root = findparent(self, RepoHistoryItem)
        self.branch_path = sub_root.branch_path
        self.branch_logid = sub_root.branch_logid
        root = findparent(self, HistoryBox)

        root.load_diff(self.branch_path, self.branch_logid)


class MenuButton(Button):
    """
    MenuButton; the buttons of menu items as history, changes,
        branches, settings or adding repo are all menubutton classes
    :popup: yes-no answer should be taken if removing an repository
        action is on the line to be sure
    :repo_path: based answer of user to delete a repository this
        path will be used.
    """
    popup = None
    repo_path = ""
    def on_press(self):
        """
        on_press; this default function, handle to show which button is select visually
            as changing background_color and on back side as changing pressed attribute.
        """
        change_all = False
        if (self.parent.repoadd_button or \
            self.parent.reporemove_button) and \
                self.uid not in [self.parent.repoadd_button.uid,
                                 self.parent.reporemove_button.uid]:
            self.background_color = .7, .7, 1, 0.3#1, 1, 2.5, 1
            self.pressed = False
            change_all = True
        if change_all:
            buttons = self.parent.parent.menu_list.children
            for but in buttons:
                if but.uid != self.uid:
                    but.background_color = .7, .7, 1, 0.3#1, 1, 1.5, 0.5
                    but.pressed = False
                    but.text = but.text.replace('ffffff','222222')
                else:
                    but.background_color = .7, .7, 1, 0.5#1, 1, 2.5, 1
                    but.pressed = True
                    but.text = but.text.replace('222222','ffffff')

    def on_release(self):
        """
        on_release, default function is just handle the removing selected
            repository from the list, if there is any selection. Before
            deletion should ask to be sure to prevent any unwanted actions.
        """
        if self.uid == self.parent.reporemove_button.uid:
            repository_list = self.parent.parent.repolstview
            repos = repository_list.children[0].children[0].children
            for repo in repos:
                if repo.children[0].children[0].pressed:
                    self.repo_path = repo.repo_path
                    content = ConfirmPopup(text="to delete repository '%s'"%repo.repo_name)
                    content.bind(on_answer=self.on_answer)
                    self.popup = Popup(title="Are you sure?",
            							content=content,
            							size_hint=(None, None),
            							size=(400,150),
            							auto_dismiss= False)
                    self.popup.open()

    def on_answer(self, instance, answer):
        if repr(answer) == "'yes'":
            root = findparent(self, RepoWatcher)
            root.remove_repo(self.repo_path)
        self.popup.dismiss()



class AddRepoButton(Button):
    """
    AddRepoButton; if want to add a repository, this button is actually pressed.
    """
    def on_press(self):
        """
        on_press; default function is for handle import operation of
            selected repository, if it is actually a git repository folder,
            .git file is checking otherwise error is displaying as popup.
        """
        selection = None
        popup = None
        text = striptags(self.text)
        if text == "Add Repo":
            selection = self.parent.parent.repoaddbox.repopath.text
            self.parent.parent.popup.dismiss()
        elif text == "Choose" and self.parent.listview.selection:
            self.parent.listview.selection
            selection = self.parent.listview.selection[0]
        if selection:
            directory = os.path.dirname(settings.REPOFILE)
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                repofile = file(settings.REPOFILE, "r")
            except IOError:
                repofile = file(settings.REPOFILE, "w")
            try:
                data = json.loads(repofile.read())
            except (IOError, TypeError, ValueError):
                data = []
            repofile.close()
            if os.path.exists(selection):
                os.chdir(selection)
                if os.path.exists(".git"):
                    repofile = file(settings.REPOFILE, "w")
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
    """
    RepoDetailButton; repository list is using this class,
        all repository on the list is clickable as button
    """

    def on_press(self):
        """
        on_press; default function is for just displaying which button/repository is pressed
        """
        pressed = self.parent.parent.repobutton.children
        pressed_area = self.parent.parent
        button_list = filter(lambda x: x != pressed_area,
                               self.parent.parent.parent.children)
        for child in pressed:
            #.9, .9, 2, 1
            child.background_color = [.7, .7, 1, 0.5]
            child.text = child.text.replace('333333', 'FFFFFF')
            child.pressed = True

        for child in button_list:
            if child != pressed_area:
                for but in child.repobutton.children:
                    # .7, .7, 1, 1
                    but.background_color = [.7, .7, 1, 0.3]
                    but.text = but.text.replace('FFFFFF', '333333')
                    but.pressed = False

    def on_release(self):
        """
        on_release; default function is for displaying repository
            detail based on the current screen.
        """
        root = findparent(self, RepoWatcher)

        screen = root.screen_manager.children[0].children[0].children[0]
        root.syncbutton.text = root.syncbutton.text.replace('CECFC6','000000')
        root.syncbutton.path = self.repo_path

        if root.history_button.pressed:
            screen.check_history(self.repo_path)

        elif root.changes_button.pressed:
            screen.changes_check(self.repo_path)

        elif root.branches_button.pressed:
            screen.branches_check(self.repo_path)

        elif root.settings_button.pressed:
            screen.settings_check(self.repo_path)

        os.chdir(settings.PROJECT_PATH)


class ChangesDiffButton(Button):
    """
    ChangesDiffButton; to show the file by file diffs this class is
        used to display changed files on a list
    """
    def on_press(self):
        """
        on_press; handle to display which file pressed.
        """
        root = findparent(self, ChangesItem)

        for l in root.parent.children:
            if hasattr(l, 'pressed') and l.pressed:
                l.pressed = False

        root.filename.text = root.filename.text.replace('777777', '000000')
        root.pressed = True

        for l in root.parent.children:
            if hasattr(l, 'pressed') and not l.pressed:
                l.filename.text = l.filename.text.replace('000000', '777777')

    def on_release(self):
        """
        on_release; diff datas are taken and placing the area.
        """
        os.chdir(self.repo_path)
        out, message, commit, outhor, date = diff_formatter(
            run_syscall('git diff %s '%self.file_name))

        screen = findparent(self, ChangesBox)

        screen.localdiffarea.text = striptags("[color=000000]%s[/color]"%out)
        os.chdir(settings.PROJECT_PATH)


class CommitButton(Button):
    """
    CommitButton, is for making difference between commit and commint&push button.
    """
    def on_press(self):
        """
        on_press; default function is for handling the committion or
            commit with push operation checking for empty description
            and commit lists handling if anything is wrong popup is
            displayed with message.
        """
        also_push = self.parent.commitpushbutton.state == 'down'
        description = self.parent.parent.parent.parent.message.text
        commits = self.parent.parent.parent.parent.uncommitted.children[0].children[0].children
        if not commits:
            popup = create_popup('Commiting...', Label(text='There is nothing to commit.'))
            popup.open()
        elif not description:
            popup = create_popup('Commiting...', Label(text='Commit message is required.'))
            popup.open()
        else:
            commit_paths = []
            repopath = ""
            for c in filter(lambda x: x.__class__ == ChangesItem().__class__, commits):
                checkbox = c.changesgroup.checkbox
                filepath = "%s/%s"%(c.changesgroup.filename.repo_path,
                                    c.changesgroup.filename.file_name)
                repopath = c.changesgroup.filename.repo_path
                if checkbox.active:
                    commit_paths.append(filepath)
            if commit_paths:
                os.chdir(repopath)
                out = run_syscall('git add %s'% ' '.join(commit_paths))
                os.chdir(repopath)
                out = run_syscall('git commit -m "%s"'% description)
                if also_push:
                    root = findparent(self, RepoWatcher)
                    branchname = root.get_activebranch(repopath)

                    os.chdir(repopath)
                    out = run_syscall('git push origin %s' % branchname)

            screen = findparent(self, ChangesBox)
            screen.changes_check(repopath)


class CommitandPushButton(ToggleButton):
    """
    CommitandPushButton; is for user friendly displaying,
        as user should know what is coming next.
    """
    def on_press(self):
        """
        on_press; default function is for changing the commit
            button label if this ToggleButton pressed.
        """
        if self.state == 'down':
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit", "Commit & Push")
            self.parent.commitbutton.width = '122dp'
        else:
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit & Push", "Commit")
            self.parent.commitbutton.width = '80dp'


class UnPushedButton(Button):
    """
    UnPushedButton, is for reversing the commit into current changes.
    """
    def on_press(self):
        """
        on_press; default function is for reversing the pressed
            commits and previous ones into current changes.

        Finding the commit number just before the pressed commit
        number then reset that previously committed log id.
        """
        sha = self.sha
        os.chdir(self.path)
        out = run_syscall('git log --oneline --pretty="%h"')
        commitlist = out.split('\n')
        prev_commit = commitlist[commitlist.index(sha)+1]
        os.chdir(self.path)
        out = run_syscall('git reset --soft %s;git reset HEAD'%prev_commit)

        root = findparent(self, ChangesBox)
        os.chdir(settings.PROJECT_PATH)


class SettingsButton(Button):
    """
    SettingsButton; is for handle the requested change operation on
        .gitignore file or remote url path
    """
    def on_press(self):
        """
        on_press, default function is for handle the change itself,
            button types help to understand what is wanted.
        """
        root = findparent(self, SettingsBox)
        button_text = striptags(self.text)
        if root.remotebutton == self:
            text = root.remote_url.text
            os.chdir(root.repo_path)
            out = run_syscall('git remote set_url origin %s'%text)
        elif root.ignorebutton == self:
            text = root.gitignore.text
            os.chdir(root.repo_path)
            out = run_syscall('echo "%s" > .gitignore'%text)

        root.settings_check(root.repo_path)
        os.chdir(settings.PROJECT_PATH)


class SyncButton(Button):
    """
    SyncButton; repositories in generally needs to update this
        button is handle that operation, by user request as pressing.
    """
    def on_press(self):
        """
        on_press; default function is handle all sync operation
            because of there is no need to show button pressing
            operation at the end popup is displayed.
        """
        root = findparent(self, RepoWatcher)

        cur_branch = root.get_activebranch(self.path)
        os.chdir(self.path)
        sys_call = "git stash clear;git stash;"
        sys_call += "git fetch origin %(cur_branch)s;"
        sys_call += "git pull origin %(cur_branch)s;"
        sys_call += "git stash pop"
        out = run_syscall(sys_call % {'cur_branch':cur_branch})
        os.chdir(settings.PROJECT_PATH)
        popup = create_popup('Syncing...', Label(text='Operation complete.'))
        popup.open()

class DiffButton(Button):
    """
    DiffButton; for more detailed view on history screen log's
        changed files diff outputs displays on an other screen,
        this button is used for that screen changing.
    """
    def select(self, *args, **kwargs):
        """
        select; default function required select function as default
        """
        pass

    def deselect(self, *args, **kwargs):
        """
        deselect; default function required deselect function as default
        """
        pass

    def on_press(self):
        """
        on_press; default function is handle the screen changing operation
        """
        root = findparent(self, RepoWatcher)
        root.show_kv('FileDiff')

    def on_release(self):
        """
        on_release; handle the data of new screen with selected file on specificly chosen log id
        """
        root = findparent(self, RepoWatcher)
        screen = findparent(self, HistoryBox)
        sha = screen.commitlabel.text
        current_screen = root.screen_manager.current_screen
        filediffbox = current_screen.children[0].children[0]
        filediffbox.repo_path = self.repo_path
        filediffbox.sha = sha.split("[size=11]")[1].split("[/size]")[0].strip()
        filediffbox.file_path = self.path
        filediffbox.diff = self.parent.textarea.text
