from __future__ import annotations
import subprocess
from pathlib import Path
class ProcessManager:
    def __init__(self): self.process:subprocess.Popen[str]|None=None
    def start(self,command:list[str],cwd:str|Path|None=None):
        self.process=subprocess.Popen(command,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);return self.process
    def stop(self,timeout:float=3):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:self.kill()
    def kill(self):
        if self.process and self.process.poll() is None:self.process.kill();self.process.wait()
    def get_exit_code(self): return self.process.poll() if self.process else None
    def cleanup(self): self.stop();self.process=None
