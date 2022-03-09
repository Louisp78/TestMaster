import subprocess
import threading

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stdout = None
        self.stderr = None

    # Basic Run method with a timeout
    def run(self, timeout=0.5):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = self.process.communicate()
            self.stdout = stdout
            self.stderr = stderr

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()