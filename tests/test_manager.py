from threading import Event
from core.test_manager import TestManager,TestState
from core.process_manager import ProcessManager
import sys
def test_manager_streams_events_and_completes():
    manager=TestManager(); done=Event()
    def task(cancel,log): log("started");done.set()
    manager.start(TestState.RUNNING_API,task); assert done.wait(1)
    import time;time.sleep(.02)
    events=list(manager.poll()); assert any(event.kind=="log" for event in events) and manager.state==TestState.COMPLETED

def test_process_manager_starts_and_reads_exit_code():
    process=ProcessManager(); process.start([sys.executable,"-c","print('ok')"]); assert process.process.wait(timeout=2)==0 and process.get_exit_code()==0; process.cleanup()
