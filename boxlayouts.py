import os
import settings
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from shortcuts import run_syscall, diff_formatter


class FileDiffBox(BoxLayout):
    diff = StringProperty()
    file_path = StringProperty()
    sha = StringProperty()

class SettingsBox(BoxLayout):
    repo_path = StringProperty()

    def get_gitignore(self, path):
        os.chdir(path)
        try:
            gitignore = run_syscall('cat .gitignore')
            self.gitignore.text = gitignore
        except CommandLineException:
            self.gitignore.text = ""
        os.chdir(settings.PROJECT_PATH)

    def get_remote(self, path):
        os.chdir(path)
        out = run_syscall('git remote -v')
        try:
            origin = 'origin'.join(filter(lambda x: x.startswith('origin'),
                                out.split("\n"))[0].split('origin')[1:]).strip()
            origin = ')'.join(origin.split("(")[:-1]).strip()
            self.remote_url.text = origin
        except IndexError:
            self.remote_url.text = ""
        os.chdir(settings.PROJECT_PATH)

    def set_repopath(self, path):
        self.repo_path = path

    def settings_check(self, path):
        self.set_repopath(path)
        self.get_remote(path)
        self.get_gitignore(path)
        os.chdir(settings.PROJECT_PATH)

class BranchesBox(BoxLayout):
    name = StringProperty()
    subject = StringProperty()
    sha = StringProperty()
    commiter = StringProperty()
    date = StringProperty()
    branches = ListProperty()

    def __init__(self, *args, **kwargs):
        super(BranchesBox, self).__init__(*args, **kwargs)
        self.name = ""
        self.subject = ""
        self.sha = ""
        self.commiter = "Repo selection needed"

    def args_converter(self, row_index, item):
        return {
            'index': row_index,
            'date': item['date'],
            'sha': item['sha'],
            'name': item['name'],
            'commiter': item['commiter'],
            'subject': item['subject']
        }

    def get_activebranch(self, path):
        os.chdir(path)
        out = run_syscall('git branch')
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")
        os.chdir(settings.PROJECT_PATH)
        return text

    def get_branches(self, path):
        text = self.get_activebranch(path)
        os.chdir(path)
        script = "git for-each-ref --format='%(committerdate:short)"
        script += " ; %(authorname) , %(refname:short),%(objectname:short)"
        script += " : %(subject)' --sort=committerdate refs/heads/"
        out = run_syscall(script).strip()
        self.branches = []
        for l in out.split("\n"):
            tmp = dict(date="", name="", sha="", commiter="", subject="")
            tmp['subject'] = l.split(':')[-1]; l = l.split(':')[0].strip()
            tmp['sha'] = l.split(',')[-1]; l = ','.join(l.split(',')[:-1])
            tmp['name'] = l.split(',')[-1]; l = l.split(',')[0].strip()
            tmp['commiter'] = l.split(';')[-1]; l = l.split(';')[0].strip()
            tmp['date'] = l
            if text and text == tmp['name'].strip():
                self.name = tmp['name'].strip()
                self.subject = tmp['subject'].strip()
                self.sha = tmp['sha'].strip()
                self.commiter = tmp['commiter'].strip()
                self.date = tmp['date'].strip()
            else:
                self.branches.append(tmp)
        os.chdir(settings.PROJECT_PATH)

    def branches_check(self, path):
        self.get_branches(path)
        os.chdir(settings.PROJECT_PATH)

class ChangesBox(BoxLayout):
    changes = ListProperty()
    unpushed = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'index': row_index,
            'file_name': item['name'],
            'repo_path': item['path']}

    def unpushed_args_converter(self, row_index, item):
        return {
            'index': row_index,
            'sha': item['sha'],
            'subject': item['subject'],
            'path': item['path']}


    def get_userinfo(self, path):
        os.chdir(path)
        text = self.userinfo.text.split('[/font]')[0] + '[/font]'
        self.message.text = ""
        name = run_syscall('git config --global user.name')
        email = run_syscall('git config --global user.email')
        text += " Uncommitted Changes[/b][/size]\n"
        text += "[size=12]%s[/size]\n"
        text += "[size=9]%s[/size][/color]"
        text = text%(name, email)
        self.userinfo.text = text
        os.chdir(settings.PROJECT_PATH)

    def get_difffiles(self, path):
        os.chdir(path)
        out = run_syscall('git status -s')
        files = filter(lambda x: x, map(lambda x: ' '.join(x.strip().split(' ')[1:]).strip(), out.split("\n")))
        self.localdiffarea.text = ""
        self.changes = []
        if files:
            for f in files:
                tmp = dict(name=f, path=path)
                self.changes.append(tmp)
        path_value = self.repopathlabel.text
        path_value.split(" ")[0]
        repo_path_text = " [color=202020][size=10]%s[/size][/color]" % path
        repo_path_text = repo_path_text.replace(run_syscall('echo $HOME'), "~")
        self.repopathlabel.text = repo_path_text
        os.chdir(settings.PROJECT_PATH)

    def get_unpushedfiles(self, path):
        os.chdir(path)
        out = run_syscall('git log origin/master..HEAD --pretty="%h - %s"')
        self.unpushed = []
        if out:
            for l in out.split("\n"):
                tmp = dict(subject="", sha="", path=path)
                tmp['subject'] = " - ".join(l.split(" - ")[1:]).strip()
                tmp['sha'] = l.split(" - ")[0].strip()
                self.unpushed.append(tmp)
        os.chdir(settings.PROJECT_PATH)

    def get_current_branch(self, path):
        os.chdir(path)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")

        self.info.text = self.info.text.split(" ")[0] + \
                           "[color=575757][size=12] Committing to %s[/size][/color]"%text
        os.chdir(settings.PROJECT_PATH)


    def get_current_branch(self, path):
        os.chdir(path)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")

        self.info.text = self.info.text.split(" ")[0] + \
                           "[color=575757][size=12] Committing to %s[/size][/color]"%text


    def get_current_branch(self, path):
        os.chdir(path)
        out = run_syscall('git branch')
        values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
        text = filter(lambda x: x.find("* ") != -1, out.split("\n"))[0].replace("* ", "")

        self.info.text = self.info.text.split(" ")[0] + \
                           "[color=575757][size=12] Committing to %s[/size][/color]"%text


    def changes_check(self, path):
        self.get_userinfo(path)
        self.get_difffiles(path)
        self.get_unpushedfiles(path)
        self.get_current_branch(path)
        os.chdir(settings.PROJECT_PATH)


class HistoryBox(BoxLayout):
    history = ListProperty()
    diff = ListProperty()

    def history_args_converter(self, row_index, item):
        return {
            'branch_index': row_index,
            'branch_commiter': item['commiter'],
            'branch_message': item['message'],
            'branch_date': item['date'],
            'branch_logid': item['logid'],
            'branch_path': item['path'],
            'diff_files': item['files']}

    def diff_args_converter(self, row_index, item):
        return {
            'row_index': row_index,
            'path': item['path'],
            'diff': item['diff'],
            'repo_path': item['repo_path']}


    def load_diff(self, path, logid):
        os.chdir(path)
        out = run_syscall('git show %s --name-only '%logid + \
                '--pretty="sha:(%h) author:(%an) date:(%ar) message:>>%s<<%n"')
        files = out.split("\n\n")[-1].strip().split("\n")
        try:
            out = run_syscall('git log %s '%logid + \
                '--pretty="sha:(%h) author:(%an) date:(%ar) message:>>%s<<%n"')
        except CommandLineException:
            out = "Error Occured"
        out, message, commit, author, date = diff_formatter(out)
        self.diff = []
        for f in files:
            out = run_syscall('git show %s %s'%(logid, f))
            tmp = dict(path=f, diff=out, repo_path=path)
            self.diff.append(tmp)

        self.commitinfo.text = message
        commitlabel_pre = self.commitlabel.text.split(' ')[0]
        self.commitlabel.text = commitlabel_pre+" [color=000000][size=11]%s[/size][/color]"%commit
        authorlabel_pre = self.authorlabel.text.split(' ')[0]
        self.authorlabel.text = authorlabel_pre+" [color=000000][size=11]%s[/size][/color]"%author
        datelabel_pre = self.datelabel.text.split(' ')[0]
        self.datelabel.text = datelabel_pre+" [color=000000][size=11]%s[/size][/color]"%date
        os.chdir(settings.PROJECT_PATH)

    def get_history(self, path):
        os.chdir(path)
        out = run_syscall('git log --pretty=format:"%h - %an , %ar : %s |||" --name-only')
        lines = out.split("\n\n")
        self.history = []
        for group in lines:
            group = group.split("|||")
            files = group[-1]
            l = "|||".join(group[:-1])
            files = files.strip().split("\n")
            tmp = dict(commiter="", message="", date="", logid="", path=path)
            tmp["logid"] = l.split(" - ")[0].strip()
            l = l.split(" - ")[1:][0].strip()
            tmp["commiter"] = l.split(" , ")[0].strip()
            l = l.split(" , ")[1:][0].strip()
            tmp["date"] = l.split(" : ")[0].strip()
            l = l.split(" : ")[1:][0].strip()
            if len(l) > 50:
                l = "%s..." % l[:50]
            tmp["message"] = l.replace("\n", " ").split('|||')[0]
            tmp["files"] = files
            self.history.append(tmp)
        plural='s' if len(self.history) > 1 else ''
        self.repohistory_count.text = "[color=000000][size=12][b]%s commit%s[/b][/size][/color]"%\
                                                (len(self.history), plural)
        os.chdir(settings.PROJECT_PATH)


    def get_diff_clear(self, path):
        self.diff = []
        self.commitinfo.text = ""
        self.commitlabel.text = self.commitlabel.text.split(' ')[0]+' '
        self.authorlabel.text = self.authorlabel.text.split(' ')[0]+' '
        self.datelabel.text = self.datelabel.text.split(' ')[0]+' '

    def check_history(self, path, keep_old = False):
        if not keep_old:
            self.get_history(path)
            self.get_diff_clear(path)
        os.chdir(settings.PROJECT_PATH)


