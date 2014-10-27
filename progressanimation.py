from kivy.clock import Clock


class ProgressAnimator(object):
    def __init__(self, progressbar, callbacks, variables):
        self.pb = progressbar
        self.pb.value = 0
        self.per = 100.0 / len(callbacks)
        self.variables = variables
        self.callbacks = callbacks
        self.index = 0
        variable = self.variables + [self.task_complete]
        Clock.schedule_once(lambda dt: callbacks[0](variable[0], variable[1]), 0.1)

    def task_complete(self):
        self.index += 1
        self.pb.value = self.index * self.per
        if self.index < len(self.callbacks):
            variable = self.variables + [self.task_complete]
            Clock.schedule_once(
                lambda dt: self.callbacks[self.index](variable[0], variable[1]), 0.1)
