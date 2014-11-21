import os
from kivy.core.text import LabelBase
from shortcuts import run_syscall

PROJECT_PATH = "/".join(os.path.realpath(__file__).split("/")[:-1])

KIVY_FONTS = [
    {
        "name": "FiraSans",
        "fn_regular": "%s/assets/fonts/FiraSans-Regular.ttf"%PROJECT_PATH,
    },
    {
        "name": "WebAwesome",
        "fn_regular": "%s/assets/fonts/fontawesome-webfont.ttf"%PROJECT_PATH,
    },
    {
        "name": "FiraSansBold",
        "fn_regular": "%s/assets/fonts/FiraSans-Bold.ttf"%PROJECT_PATH,
    }
]

for font in KIVY_FONTS:
    LabelBase.register(**font)

KIVY_DEFAULT_FONT = "FiraSans"
KIVY_ICONIC_FONT = "WebAwesome"
KIVY_DEFAULT_BOLD_FONT = "FiraSansBold"

cmd = "echo $HOME"
out = run_syscall(cmd)
REPOFILE = "%s/.kivyrepowatcher/repowatcher" % out.rstrip()