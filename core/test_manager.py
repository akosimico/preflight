from __future__ import annotations
from enum import StrEnum
from queue import Queue,Empty
from threading import Event as StopEvent,Thread
from collections.abc import Callable
from core.events import Event
class TestState(StrEnum):
    __test__=False
    IDLE="IDLE"; CONNECTING="CONNECTING"; DISCOVERING="DISCOVERING"; RUNNING_API="RUNNING_API"; RUNNING_LOAD="RUNNING_LOAD"; RUNNING_SECURITY="RUNNING_SECURITY"; EVALUATING="EVALUATING"; COMPLETED="COMPLETED"; FAILED="FAILED"; CANCELLED="CANCELLED"
class TestManager:
    __test__=False
    def __init__(self): self.state=TestState.IDLE;self.events:Queue[Event]=Queue();self._cancel=StopEvent();self._thread:Thread|None=None
    def start(self,state:TestState,task:Callable[[StopEvent,Callable[[str],None]],None]):
        if self._thread and self._thread.is_alive(): raise RuntimeError("A test run is already active")
        self._cancel.clear();self.state=state;self.events.put(Event("state",{"state":state}))
        def worker():
            try: task(self._cancel,lambda message:self.events.put(Event("log",{"message":message})));self.state=TestState.CANCELLED if self._cancel.is_set() else TestState.COMPLETED
            except Exception as error: self.state=TestState.FAILED;self.events.put(Event("log",{"message":str(error),"severity":"error"}))
            finally:self.events.put(Event("state",{"state":self.state}))
        self._thread=Thread(target=worker,daemon=True);self._thread.start()
    def cancel(self): self._cancel.set();self.events.put(Event("log",{"message":"Cancellation requested."}))
    def poll(self):
        while True:
            try: yield self.events.get_nowait()
            except Empty: return
