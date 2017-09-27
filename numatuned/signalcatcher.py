import signal

class SignalCatcher:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Gets called when we catch a certain signal"""
        print('Got signal', signum, frame)
        self.kill_now = True
