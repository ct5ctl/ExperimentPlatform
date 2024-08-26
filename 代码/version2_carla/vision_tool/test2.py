import threading,sys,time,os,signal

class SimulationTimeoutTimer:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.timer = None
        self.lock = threading.Lock()

    def _run(self):
        with self.lock:
            self.timer = None
            self.callback()

    def start(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(self.timeout, self._run)
            self.timer.start()

    def reset(self):
        self.start()
        
if __name__ == '__main__':
    def exit_program():
        print("Exiting program due to timeout.")
        os.kill(os.getpid(), signal.SIGTERM)  
        
    timeouttimer = SimulationTimeoutTimer(5, exit_program)
    timeouttimer.start()
    try:
        while True:
            time.sleep(0.01) 
    except KeyboardInterrupt:
        print("Interrupted by user")