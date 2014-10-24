import os
import re
from subprocess import Popen, PIPE
from kivy.uix.popup import Popup

def run_syscall(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()

def striptags(text):
    return re.sub(r'\[[^>]*?\]', '', text)

def create_popup(title, content):
    popup = Popup(title=title, content=content,
                  size_hint=(None, None), size=(300, 100))
    return popup

def diff_formatter(text):
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
