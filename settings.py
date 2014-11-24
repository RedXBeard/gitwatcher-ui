import os
import kivy
from kivy.core.text import LabelBase
from shortcuts import run_syscall

PATH_SEPERATOR = '\\' if os.path.realpath(__file__).find('\\') != -1 else '/'

PROJECT_PATH = PATH_SEPERATOR.join(os.path.realpath(__file__).\
                                    split(PATH_SEPERATOR)[:-1])

KIVY_FONTS = [
    {
        "name": "FiraSans",
        "fn_regular": "%(pp)s%(ps)sassets%(ps)sfonts%(ps)sFiraSans-Regular.ttf"%{'pp':PROJECT_PATH,
                                                                                 'ps':PATH_SEPERATOR},
    },
    {
        "name": "WebAwesome",
        "fn_regular": "%(pp)s%(ps)sassets%(ps)sfonts%(ps)sfontawesome-webfont.ttf"%{'pp':PROJECT_PATH,
                                                                                    'ps':PATH_SEPERATOR},
    },
    {
        "name": "FiraSansBold",
        "fn_regular": "%(pp)s%(ps)sassets%(ps)sfonts/FiraSans-Bold.ttf"%{'pp':PROJECT_PATH,
                                                                         'ps':PATH_SEPERATOR},
    }
]

for font in KIVY_FONTS:
    LabelBase.register(**font)

KIVY_DEFAULT_FONT = "FiraSans"
KIVY_ICONIC_FONT = "WebAwesome"
KIVY_DEFAULT_BOLD_FONT = "FiraSansBold"

cmd = "echo $HOME"
out = run_syscall(cmd)
REPOFILE = "%(out)s%(ps)s.kivyrepowatcher%(ps)srepowatcher" % {'out': out.rstrip(),
                                                               'ps': PATH_SEPERATOR}
KIVY_VERSION = kivy.__version__