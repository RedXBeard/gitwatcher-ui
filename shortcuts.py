import os
import re
from subprocess import Popen, PIPE
from kivy.uix.popup import Popup

def run_syscall(cmd):
    """
    run_syscall; handle sys calls this function used as shortcut.

    ::cmd: String, shell command is expected.
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()

def striptags(text):
    """
    striptags; markuped text should be cleared to use
        most of times this function is used as shortcuts.
    ::text: String; markuped text is expected
    """
    return re.sub(r'\[[^>]*?\]', '', text)

def create_popup(title, content):
    """
    create_popup; couple of actions' result displayed as popup,
        this function used as shortcut.
    ::title: String.
    ::content: Label, kivy Label class expected.
    """
    popup = Popup(title=title, content=content,
                  size_hint=(None, None), size=(300, 100))
    return popup

def diff_formatter(text):
    """
    diff_formatter; diff text formats with this function lines starts with '+'
        line colored with green if starts with '-' then line should be
        colored with red others should keep with black. diff datas such as
        commiter, commit date, commit message, commit log id short one are
        collecting and result returned.
    ::text: String
    """
    def replacer(text, search, color):
        return text
        # convertion should wait for a while.
        result_text = ""
        location = 0

        while location != -1:
            tmp_location = text.find(search)
            if tmp_location != -1:
                result_text += text[:tmp_location]
                line_end = text[tmp_location + 2:].find("\n")
                if line_end > 0:
                    result_text += "\n[color=%s]%s[/color]" % \
                                   (color,
                                    text[tmp_location + 1:tmp_location + 2 + line_end])
                else:
                    result_text += "\n[color=%s]%s[/color]" % \
                                   (color, text[tmp_location + 1:])
                    text = ""
                location = tmp_location + 2 + line_end
                text = text[location:]
            else:
                result_text += text
                location = -1
        return result_text

    green = "\n+"
    red = "\n-"
    tmp_text = text
    result_text = replacer(replacer(tmp_text, green, "00ff00"), red, "ff0000")
    commit, merge, author, date = "", "", "", ""
    data = '<<\n'.join(result_text.split("<<\n")[:1]).strip()
    if data.startswith('sha'):
        diff = '<<\n'.join(result_text.split("<<\n")[1:]).strip()
        message = data.split('>>')[1].strip()
        commit = data.split('author:')[0].split('sha:(')[1].replace(')','').strip()
        author = data.split('date:')[0].split('author:(')[1].replace(')','').strip()
        date = data.split('message:')[0].split('date:(')[1].replace(')','').strip()
    else:
        diff = data
        message, commit, author, date = "","","",""
    return diff, message, commit, author, date

def findparent(curclass, targetclass):
    """
    findparent; each classes has a parent, in an action
        parent classes methods in generally are used to
        reach needed class this function is used as shortcut.
        until target class and current class names are equal
        recursion continues.
    ::curclass: class, current class
    ::targetclass: class, target class
    """
    reqclass = curclass
    if type(targetclass) in [unicode, str]:
        targetclass_name = targetclass
    else:
        targetclass_name = str(targetclass().__class__).\
                                    split('.')[1].replace("'>","")
    while True:
        if str(reqclass.__class__).split('.')[1].\
                                replace("'>","") == targetclass_name:
            break
        elif str(reqclass.__class__).split('.')[1].replace("'>","") == 'core':
            reqclass = None
            break

        reqclass = reqclass.parent
    return reqclass