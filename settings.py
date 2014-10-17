import os
from kivy.core.text import LabelBase

KIVY_FONTS = [
    {
        "name": "FiraSans",
        "fn_regular": "assets/fonts/FiraSans-Regular.ttf"
    },
    {
        "name": "WebAwesome",
        "fn_regular": "assets/fonts/fontawesome-webfont.ttf"
    }
]

for font in KIVY_FONTS:
    LabelBase.register(**font)

KIVY_DEFAULT_FONT = "FiraSans"
PROJECT_PATH = "/".join(os.path.realpath(__file__).split("/")[:-1])
