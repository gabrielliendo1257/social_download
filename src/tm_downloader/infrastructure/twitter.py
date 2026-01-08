import os
import signal
import subprocess


class ProcessHandle:
    def __init__(self, cmd):
        self.proc = subprocess.Popen(
            cmd,
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    def pid(self):
        return self.proc.pid

    def is_running(self):
        return self.proc.poll() is None

    def stop(self):
        if self.is_running():
            os.killpg(self.proc.pid, signal.SIGTERM)

    def kill(self):
        if self.is_running():
            os.killpg(self.proc.pid, signal.SIGKILL)
