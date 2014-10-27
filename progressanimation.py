from kivy.clock import Clock


class ProgressAnimator(object):
    """
    This class handles the animation of a 'ProgressBar' instance given a list
    of functions that do the real work. Each of these functions need to accept
    a single 'callback' parameter specifying the function to call when done.
    """
    def __init__(self, progressbar, callbacks, variables):
        self.pb = progressbar  # Reference to the progress bar  to update
        self.pb.value = 0
        self.per = 100.0 / len(callbacks)
        self.variables = variables
        self.callbacks = callbacks  # A list of callback functions doing work
        self.index = 0  # The index of the callback being executed
        variable = self.variables + [self.task_complete]
        Clock.schedule_once(lambda dt: callbacks[0](variable[0], variable[1]), 0.1)

    def task_complete(self):
        """ The last called heavy worker is done. See if we have any left """
        self.index += 1
        self.pb.value = self.index * self.per
        if self.index < len(self.callbacks):
            variable = self.variables + [self.task_complete]
            Clock.schedule_once(
                lambda dt: self.callbacks[self.index](variable[0], variable[1]), 0.1)