import os
import settings
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from shortcuts import run_syscall, diff_formatter, findparent
from progressanimation import ProgressAnimator
from main import RepoWatcher


class FileDiffBox(BoxLayout):
    """
    FieDiffBox, responsable for displaying only one file full diff

    ::diff: String, file all diff data is kept
    ::file_path: String, path of file representation
    ::sha: String, commit sha data is kept
    """
    diff = StringProperty()
    file_path = StringProperty()
    sha = StringProperty()

class SettingsBox(BoxLayout):
    """
    SettingsBox, Settings menu screen displaying area

    served calls; get_gitignore, get_remote, set_repopath, settings_check
    """

    repo_path = StringProperty('')

    def get_gitignore(self, path, callback=None):
        """
        get_gitignore; getting .gitignore file to display

        :path: repository existing path is given
        :callback: to represent progression callback method can be given.
        """
        if path:
            os.chdir(path)
            try:
                gitignore = run_syscall('cat .gitignore')
                self.gitignore.text = gitignore
            except CommandLineException:
                self.gitignore.text = ""
            os.chdir(settings.PROJECT_PATH)
        else:
            self.gitignore.text = ""

        if callback:
            callback()

    def get_remote(self, path, callback=None):
        """
        get_remote; repository origin remote path is served

        :path: repository existing path is given
        :callback: to represent progression callback method can be given.
        """
        if path:
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
        else:
            self.remote_url.text = ""

        if callback:
            callback()

    def set_repopath(self, path, callback=None):
        """
        set_repopath; to use later for any reason in related screen the path of
            selected repository will be saved in an attribute
        :path: repository full path
        """
        self.repo_path = path
        if callback:
            callback()

    def settings_check(self, path):
        """
        settings_check; if settings menu is selected somehow,
            data of settings box should be updated.
            All required functions calls are in one call.
            To represent progression main app class'
            progressbar attribute is used.
        :path: repository existing path is given
        """
        root = findparent(self, RepoWatcher)
        tasks = [root.get_branches,
                 self.set_repopath,
                 self.get_remote,
                 self.get_gitignore]
        ProgressAnimator(root.pb, tasks, [path])
        os.chdir(settings.PROJECT_PATH)


class BranchesBox(BoxLayout):
    """
    BranchesBox; To display repository branches this class is used

    ::name: String; represent current branch name.
    ::subject: String; represent current branches last commit message.
    ::sha: String; represent current branch last commit log id.
    ::commiter: String; represent current branch last commiter as
        first and last name if they are set.
    ::date: String; represent current branch last commit date.
    ::branches: List; represent all local branches except current branch.

    served calls; get_branches, branches_check
    """
    name = StringProperty("")
    subject = StringProperty("")
    sha = StringProperty("")
    commiter = StringProperty("Repo selection needed")
    date = StringProperty("")
    branches = ListProperty("")
    repo_path = StringProperty("")
    rename = BooleanProperty(False)
    newbranch = BooleanProperty(False)

    def args_converter(self, row_index, item):
        """
        args_converter; To display branch list, an converter
            is necessary for kivy Factory.
        """
        return {
            'index': row_index,
            'date': item['date'],
            'sha': item['sha'],
            'name': item['name'],
            'commiter': item['commiter'],
            'subject': item['subject'],
        }

    def remove_branch(self, path, branch_name):
        """
        remove_branch; handle the branch -D command line
            expression of deletion a branch which is selected.
        :path: repository full path
        :branch_name: branch name, wanted to delete.
        """
        os.chdir(path)
        out = run_syscall('git branch -D %s'%branch_name)


    def remove_rename_widget(self, path, callback=None):
        """
        remove_rename_widget; handle the currentbranchbox widget order to
            replace label type of branch name part to editable text
        :path: repository full path
        """
        try:
            cur_branchbox = self.currentbranchlabelbox

            label = self.repobranchlabel
            edit = self.repobranchedit
            sha = self.repobranchsha
            text = self.repobranchtext
            button = self.branchmenubutton

            rename_widgets = [edit, sha, text, button]
            nonrename_widgets = [label, sha, text, button]
            all = [label, edit, sha, text, button]
            if not self.rename:
                for w in all:
                    cur_branchbox.remove_widget(w)

                for w in nonrename_widgets:
                    cur_branchbox.add_widget(w)
            else:
                for w in all:
                    cur_branchbox.remove_widget(w)

                for w in rename_widgets:
                    cur_branchbox.add_widget(w)
        except Exception, e:
            print e

        if callback:
            callback()

    def remove_newbranch_widget(self, path, callback=None):
        """
        remove_newbranch_widget; is for remove the newbranch boxlayout and
            redesign branchesbox layout itself.
        """
        try:
            cur_branchbox = self.currentbranchbox
            if not self.newbranch:
                for child in self.currentbranchbox.children:
                    if hasattr(child, 'name') and child.name == "newbranch":
                        cur_branchbox.remove_widget(child)
                        self.currentbranchbox.height -= 30
                        self.currentbranchboxparent.height -= 30
                        break

            else:
                self.currentbranchbox.height += 30
                self.currentbranchboxparent.height += 30
                cur_branchbox.add_widget(self.newbranchbox)
        except Exception, e:
            print e

        if callback:
            callback()

    def set_repopath(self, path, callback=None):
        """
        set_repopath; to set the repository path,
            to the base class of the screen.
        """
        self.repo_path = path
        if callback:
            callback()

    def clear_buttonactions(self, path, callback=None):
        """
        clear_buttonactions, to clear all BranchMenuButton's actions
        :path: as ruled, repository path
        :calback: to display progression callback could be used.
        """
        listed_buttons = set([self.branchmenubutton])
        for branchitem in self.branchlist.children[0].children[0].children:
            if str(branchitem.__class__).\
                        split('.')[1].replace('\'>','') == 'BranchesItem':
                listed_buttons.add(branchitem.children[1].children[0])
        for bi in listed_buttons:
            if bi != self and hasattr(bi, 'bubble'):
                bi.remove_widget(bi.bubble)
                delattr(bi, 'bubble')
                bi.state = 'normal'
        if callback:
            callback()

    def get_branches(self, path, callback=None):
        """
        get_branches; To collect branches of selected repository
            and separate current and others.
        :path: repository path.
        :calback: to display progression callback could be used.
        """
        if path:
            root = findparent(self, RepoWatcher)

            text = root.get_activebranch(path)
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
        else:
            self.branches = []
            self.name = ""
            self.subject = ""
            self.sha = ""
            self.commiter = ""
            self.date = ""

        if callback:
            callback()

    def branches_check(self, path):
        """
        brnaches_check; When branches button is pressed data of
            related screen should be updated, required
            function calls are in one.
        :path: repository path.
        """
        root = findparent(self, RepoWatcher)
        tasks = [root.get_branches,
                 self.set_repopath,
                 self.get_branches,
                 self.clear_buttonactions,
                 self.remove_newbranch_widget,
                 self.remove_rename_widget,]
        ProgressAnimator(root.pb, tasks, [path])
        os.chdir(settings.PROJECT_PATH)

class ChangesBox(BoxLayout):
    """
    ChangesBox; Changes button is pressed,
        screen representation is used this class.
    ::changes: list; Collect 'git status' call of selected repository.
    ::unpushed: list; Collect all unpushed commits.
    """
    changes = ListProperty([])
    unpushed = ListProperty([])

    def args_converter(self, row_index, item):
        """
        args_converter; List displaying needs this kind of converter,
            returns list dictionary, all indexes keys represents
            one class attributes. Key names given by the attributes of
            related listitem classes.
        changes attribute is this function's base.
        """
        return {
            'index': row_index,
            'file_name': item['name'],
            'repo_path': item['path']}

    def unpushed_args_converter(self, row_index, item):
        """
        args_converter; List displaying needs this kind of converter,
            returns list dictionary, all indexes keys represents
            one class attributes. Key names given by the attributes of
            related listitem classes.
        unpushed attribute is this function base.
        """
        return {
            'index': row_index,
            'sha': item['sha'],
            'subject': item['subject'],
            'path': item['path']}


    def get_userinfo(self, path, callback=None):
        """
        get_userinfo; collects repository information, user's comitter name,
            last name, email address, path of repository and such
        :path: repository path as string.
        :callback: if progression is wanted callback could be used.
        """
        if path:
            os.chdir(path)
            text = self.userinfo.text.split('[/font]')[0] + '[/font]'
            self.message.text = ""
            name = run_syscall('git config --global user.name')
            email = run_syscall('git config --global user.email')
            text += " Uncommitted Changes[/font][/size]\n"
            text += "[size=10]%s[/size]\n"
            text += "[size=9]%s[/size][/color]"
            text = text%(name, email)
            self.userinfo.text = text
            os.chdir(settings.PROJECT_PATH)
        else:
            self.userinfo.text = self.userinfo.text.\
                                            split('[/font]')[0]+'[/font]'
            self.message.text = ""

        if callback:
            callback()

    def get_difffiles(self, path, callback=None):
        """
        get_difffiles; representation of 'git status' call results as list.

        :path: repository path as string.
        :callback: if progression is wanted callback could be used.
        changes attribute is used to fill data.
        """
        if path:
            os.chdir(path)
            out = run_syscall('git status -s')
            files = filter(lambda x: x,
                                map(lambda x:
                                        ' '.join(x.strip().\
                                                split(' ')[1:]).strip(),
                                    out.split("\n")))
            self.localdiffarea.text = ""
            self.changes = []
            if files:
                for f in files:
                    tmp = dict(name=f, path=path)
                    self.changes.append(tmp)
            path_value = self.repopathlabel.text
            path_value.split(" ")[0]
            repo_path_text = " [color=202020][size=10]%s[/size][/color]" % path
            repo_path_text = repo_path_text.\
                                    replace(run_syscall('echo $HOME'), "~")
            self.repopathlabel.text = unicode(repo_path_text)
            os.chdir(settings.PROJECT_PATH)
        else:
            self.changes = []
            self.localdiffarea.text = ""
            self.repopathlabel.text = ""

        if callback:
            callback()

    def get_unpushedcommits(self, path, callback=None):
        """
        get_unpushedcommits; collect unpushed commits of repository.
        :path: repository path as string.
        :callback: if progression is wanted callback could be used.
        unpushed attriute is used to fill with data.
        """
        if path:
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
        else:
            self.unpushed = []

        if callback:
            callback()

    def get_current_branch(self, path, callback=None):
        """
        get_current_branch; to display which branch those filled
            changes will be committed or committed & pushed
        :path: repository path as string.
        :callback: if progression is wanted callback could be used.
        """
        if path:
            os.chdir(path)
            out = run_syscall('git branch')
            values = map(lambda x: x.replace("* ", "").strip(), out.split("\n"))
            text = filter(lambda x: x.find("* ") != -1,
                                        out.split("\n"))[0].replace("* ", "")

            self.info.text = \
                self.info.text.split(" ")[0] + \
                "[color=575757][size=12] Committing to %s[/size][/color]"%text
            os.chdir(settings.PROJECT_PATH)
        else:
            self.info.text = self.info.text.split(" ")[0] + " "

        if callback:
            callback()

    def changes_check(self, path):
        """
        changes_check; If changes button is pressed, with
            repository path information, related screen
            data/s should be updated
        :path: repository path as string.
        """
        root = findparent(self, RepoWatcher)
        tasks = [root.get_branches,
                 self.get_userinfo,
                 self.get_difffiles,
                 self.get_unpushedcommits,
                 self.get_current_branch]
        ProgressAnimator(root.pb, tasks, [path])
        os.chdir(settings.PROJECT_PATH)


class HistoryBox(BoxLayout):
    """
    HistoryBox; History button related screen is using this class
    ::history: list; list representation of 'git log' out of selected repository
    ::diff: list; list representation of each file of selected commit's
    """
    history = ListProperty([])
    diff = ListProperty([])

    def history_args_converter(self, row_index, item):
        """
        history_args_converter; history data of this class' list
            representation of kivy Factory class needs this function
        """
        return {
            'branch_index': row_index,
            'branch_commiter': item['commiter'],
            'branch_message': item['message'],
            'branch_date': item['date'],
            'branch_logid': item['logid'],
            'branch_path': item['path'],
            'diff_files': item['files']}

    def diff_args_converter(self, row_index, item):
        """
        diff_args_converter; diff data of this class' list
            representation of kivy Factory class needs this function
        """
        return {
            'row_index': row_index,
            'path': item['path'],
            'diff': item['diff'],
            'repo_path': item['repo_path']}


    def load_diff(self, path, logid, callback=None):
        """
        load_diff; returns repository's selected history's diff
            datas as commiter, date, logid shoter version, commit message
        :path: repository path.
        :logid: history short log id
        :callback: if progression wanted to show, this can be used.
        """
        if path:
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
            self.commitlabel.text = commitlabel_pre+\
                            " [color=000000][size=11]%s[/size][/color]"%commit
            authorlabel_pre = self.authorlabel.text.split(' ')[0]
            self.authorlabel.text = authorlabel_pre+\
                            " [color=000000][size=11]%s[/size][/color]"%author
            datelabel_pre = self.datelabel.text.split(' ')[0]
            self.datelabel.text = datelabel_pre+\
                            " [color=000000][size=11]%s[/size][/color]"%date
            os.chdir(settings.PROJECT_PATH)
        else:
            self.diff = []
            self.commitinfo.text = ""
            self.commitlabel.text = ""
            self.authorlabel.text = ""
            self.datelabel.text = ""

        if callback:
            callback()

    def get_history(self, path, callback=None):
        """
        get_history; selected repository all log data is
            collected and history attribute is filled with them.
        :path: repository path.
        :callback: if progression wanted to show, this can be used.
        """
        if path:
            os.chdir(path)
            out = run_syscall('git log --pretty=format:">%h - %an , %ar : %s |||" --name-only')
            lines = out.split("\n>")
            self.history = []
            for group in lines:
                group = group.split("|||")
                files = group[-1]
                l = "|||".join(group[:-1])
                files = files.strip().replace("\n", " ").strip().split(" ")
                tmp = dict(commiter="", message="", date="", logid="", path=path)
                tmp["logid"] = l.split(" - ")[0].replace(">","").strip()
                l = " - ".join(l.split(" - ")[1:]).strip()
                tmp["commiter"] = l.split(" , ")[0].strip()
                l = " , ".join(l.split(" , ")[1:]).strip()
                tmp["date"] = l.split(" : ")[0].strip()
                l = " : ".join(l.split(" : ")[1:]).strip()
                tmp["message"] = l.replace("\n", " ").split('|||')[0]
                tmp["files"] = files
                self.history.append(tmp)
            plural='s' if len(self.history) > 1 else ''
            text = "[color=000000][size=12]"
            text += "[font=assets/fonts/FiraSans-Bold.ttf]%s commit%s[/font]"
            text += "[/size][/color]"
            self.repohistory_count.text = text % (len(self.history), plural)
            os.chdir(settings.PROJECT_PATH)
        else:
            self.history = []
            self.repohistory_count.text = ""

        if callback:
            callback()


    def get_diff_clear(self, path, callback=None):
        """
        get_diff_clear; diff area data cleaner,
            texts are sets to empty strings
        :path: repository path.
        :callback: if progression wanted to show, this can be used.
        """
        self.diff = []
        self.commitinfo.text = ""
        self.commitlabel.text = self.commitlabel.text.split(' ')[0]+' '
        self.authorlabel.text = self.authorlabel.text.split(' ')[0]+' '
        self.datelabel.text = self.datelabel.text.split(' ')[0]+' '
        if callback:
            callback()

    def check_history(self, path, keep_old = False):
        """
        check_history; If history button is pressed, with
            repository path information, related screen
            data/s should be updated
        :path: repository path.
        :keep_old: previous screen data can be wanted to keep
        """
        root = findparent(self, RepoWatcher)
        if not keep_old:
            tasks = [root.get_branches,
                     self.get_history,
                     self.get_diff_clear]
            ProgressAnimator(root.pb, tasks, [path])
        os.chdir(settings.PROJECT_PATH)


