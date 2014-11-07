from kivy.uix.bubble import Bubble
from kivy.properties import BooleanProperty

class NewSwitchRename(Bubble):
    newbranch_disabled = BooleanProperty(False)
    rename_disabled = BooleanProperty(False)
    switch_disabled = BooleanProperty(False)
    delete_disabled = BooleanProperty(False)