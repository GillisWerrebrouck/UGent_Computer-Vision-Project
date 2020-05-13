import signal

class GracefulKiller:
    kill_now = False

    def __init__(self, on_kill=None):
        """
        Create a watch for killing the process.

        Parameters
        ----------
        - on_kill -- The function to call when the process is killed.
        """
        self._on_kill = on_kill
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)


    def exit_gracefully(self, signum, frame):
        """
        Event handler for kill signals.
        """
        self.kill_now = True

        if self._on_kill is not None:
            self._on_kill()
        else:
            print('No handler for killed process given')
