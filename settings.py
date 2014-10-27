import os
from kivy.core.text import LabelBase
from shortcuts import run_syscall

KIVY_FONTS = [
    {
        "name": "FiraSans",
        "fn_regular": "assets/fonts/FiraSans-Regular.ttf",
        "fn_bold": "assets/fonts/FiraSans-Bold.ttf",
    },
    {
        "name": "WebAwesome",
        "fn_regular": "assets/fonts/fontawesome-webfont.ttf",
    }
]

for font in KIVY_FONTS:
    LabelBase.register(**font)

KIVY_DEFAULT_FONT = "FiraSans"
KIVY_ICONIC_FONT = "WebAwesome"
PROJECT_PATH = "/".join(os.path.realpath(__file__).split("/")[:-1])

cmd = "echo $HOME"
out = run_syscall(cmd)
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()