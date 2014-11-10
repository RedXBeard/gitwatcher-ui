from kivy.clock import Clock


class ProgressAnimator(object):
    """
    ProgressAnimator; main class progressbar attribute is used.
        Scheduled as calling only one and each function callback
        runs for next function and keeps that way until the last.
    """

    def __del__(self, *args, **kwargs):
        pass

    def __init__(self, progressbar, callbacks, variables):
        self.pb = progressbar
        self.pb.value = 0
        self.per = 100.0
        if len(callbacks):
            self.per = 100.0 / len(callbacks)
        self.variables = variables
        self.callbacks = callbacks
        self.index = 0
        variable = self.variables + [self.task_complete]
        print "progress called init"
        Clock.schedule_once(lambda dt: self.callbacks[0](variable[0],
                                                         variable[1]), 1)

    def task_complete(self):
        """
        task_complete; functions last callback method is actually this function,
            by this way the next method is called on call list.
        """
        print "process called complete : %s"%self.index
        self.index += 1
        self.pb.value = self.index * self.per
        if self.index < len(self.callbacks):
            variable = self.variables + [self.task_complete]
            Clock.schedule_once(
                lambda dt: self.callbacks[self.index](variable[0], variable[1]), 0.01)
        else:
            self.pb.value = 0
