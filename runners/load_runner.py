from __future__ import annotations
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor,as_completed
from threading import Event
from time import perf_counter
import statistics,httpx
PROFILES={"Smoke":(1,5),"Normal":(5,20),"Load":(20,100),"Stress":(50,200),"Spike":(100,100),"Endurance":(10,500)}
@dataclass(frozen=True)
class LoadSummary: requests:int; successes:int; failures:int; rps:float; average_ms:float; p50_ms:float; p95_ms:float; p99_ms:float; error_rate:float
def run_load(url:str,users:int=5,requests:int=20,cancel:Event|None=None)->LoadSummary:
    cancel=cancel or Event(); times=[];successes=0;started=perf_counter()
    def request():
        at=perf_counter()
        try:return httpx.get(url,timeout=10).is_success,(perf_counter()-at)*1000
        except httpx.HTTPError:return False,(perf_counter()-at)*1000
    with ThreadPoolExecutor(max_workers=users) as pool:
        futures=[pool.submit(request) for _ in range(requests) if not cancel.is_set()]
        for future in as_completed(futures): ok,elapsed=future.result();successes+=ok;times.append(elapsed)
    total=len(times);quantile=lambda p:statistics.quantiles(times,n=100)[int(p)-1] if len(times)>=2 else (times[0] if times else 0)
    return LoadSummary(total,successes,total-successes,round(total/(perf_counter()-started),2) if total else 0,round(statistics.mean(times),1) if times else 0,round(quantile(50),1),round(quantile(95),1),round(quantile(99),1),round((total-successes)/total*100,2) if total else 0)
