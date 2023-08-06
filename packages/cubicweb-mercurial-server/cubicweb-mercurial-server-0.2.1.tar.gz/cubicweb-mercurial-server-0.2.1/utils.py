from mercurial import ui

class mscui(ui.ui):
    """ inhibit stdout output and
    keep the last output around.
    Handy when test-debugging ...
    """
    def __init__(self, *args):
        super(mscui, self).__init__(*args)
        self._output = []

    def write(self, *args, **opts):
        self._output.extend(args)

    def lastoutput(self):
        return self._output[-1]
