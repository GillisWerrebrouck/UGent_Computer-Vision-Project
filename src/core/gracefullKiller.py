import signal
from time import sleep

from core.logger import get_root_logger

class GracefulKiller:

    def __init__(self, processes_to_watch = []):
        """
        Create a watch for sudden exits of the given processes. This will kill
        all other process in the list as well as the parent process.

        Parameters
        ----------
        - processes_to_watch -- The processes to start and watch for unexpected termination.
        - on_kill -- The function to call when the process is killed.
        """
        self._logger = get_root_logger()
        self._processes = processes_to_watch
        self._pids = []

        # attach the kill signal to listen for
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        # start the child processes
        self.start_processes()


    def start_processes(self):
        try:
            for process in self._processes:
                process.start()
                self._pids.append(process.pid)

            while True:
                self._logger.info(f'Checking processes state, PIDs: {self._pids}')
                for process in self._processes:
                    if not process.is_alive():
                        self._logger.info(f'Process with PID {process.pid} died, killing the others')
                        self.exit_gracefully(signal.SIGTERM, None)

                sleep(0.5)
        except Exception as err:
            self._logger.error(err)
            self.exit_gracefully(signal.SIGTERM, None)


    def exit_gracefully(self, signum, frame):
        """
        Event handler for kill signals.
        """
        for process in self._processes:
            process.kill()
            process.join()

        # graceful kill the global process
        exit(0)
