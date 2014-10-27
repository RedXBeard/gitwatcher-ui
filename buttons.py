import os
import settings
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from shortcuts import create_popup, run_syscall, diff_formatter, \
                        striptags, findparent
from listitems import ChangesItem, RepoHistoryItem
from boxlayouts import HistoryBox, SettingsBox, ChangesBox
from main import RepoWatcher


class HistoryButton(Button):
    def on_press(self):
        root = findparent(self, RepoHistoryItem)

        for l in root.parent.children:
            if l.pressed:
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
            buttons = [l.button1, l.button2, l.button3, l.button4]
            if l.pressed:
                for b in buttons:
                    b.text = b.text.replace('=777777', '=000000')
            else:
                for b in buttons:
                    b.text = b.text.replace('=000000','=777777')

    def on_release(self):
        sub_root = findparent(self, RepoHistoryItem)
        self.branch_path = sub_root.branch_path
        self.branch_logid = sub_root.branch_logid
        root = findparent(self, HistoryBox)

        root.load_diff(self.branch_path, self.branch_logid)


class MenuButton(Button):
    def on_press(self):
        if self.state == "down":
            if self.parent.repoadd_button and \
                    self.uid != self.parent.repoadd_button.uid:
                self.background_color = .7, .7, 1, 0.3#1, 1, 2.5, 1
                self.pressed = False

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
        root = self.parent.parent.parent.parent.parent
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
            #.9, .9, 2, 1
            child.background_color = [.7, .7, 1, 0.5]
            child.text = child.text.replace('333333', 'FFFFFF')
            child.pressed = True

        for child in unpressed_button_list:
            for but in child.repobutton.children:
                # .7, .7, 1, 1
                but.background_color = [.7, .7, 1, 0.3]
                but.text = but.text.replace('FFFFFF', '333333')
                but.pressed = False

    def on_release(self):
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
    def on_press(self):
        os.chdir(self.repo_path)
        out, message, commit, outhor, date = diff_formatter(
            run_syscall('git diff %s '%self.file_name))

        screen = findparent(self, ChangesBox)

        screen.localdiffarea.text = striptags("[color=000000]%s[/color]"%out)
        os.chdir(settings.PROJECT_PATH)

    def on_release(self):
        root = findparent(self, ChangesItem)

        for l in root.parent.children:
            if l.pressed:
                l.pressed = False

        root.filename.text = root.filename.text.replace('777777', '000000')
        root.pressed = True

        for l in root.parent.children:
            if not l.pressed:
                l.filename.text = l.filename.text.replace('000000', '777777')


class CommitButton(Button):
    def on_press(self):
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
    def on_press(self):
        if self.state == 'down':
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit", "Commit & Push")
            self.parent.commitbutton.width = '122dp'
        else:
            text = self.parent.commitbutton.text
            self.parent.commitbutton.text = text.replace("Commit & Push", "Commit")
            self.parent.commitbutton.width = '80dp'


class UnPushedButton(Button):
    def on_press(self):
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
    def on_press(self):
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
    def on_press(self):
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
    def select(self, *args, **kwargs):
        pass

    def deselect(self, *args, **kwargs):
        pass

    def on_press(self):
        root = findparent(self, RepoWatcher)
        screen = findparent(self, HistoryBox)

        sha = screen.commitlabel.text
        root.show_kv('FileDiff')
        current_screen = root.screen_manager.current_screen
        filediffbox = current_screen.children[0].children[0]
        filediffbox.repo_path = self.repo_path
        filediffbox.sha = sha.split("[size=11]")[1].split("[/size]")[0].strip()
        filediffbox.file_path = self.path
        filediffbox.diff = self.parent.textarea.text
