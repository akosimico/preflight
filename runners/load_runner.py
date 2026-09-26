from __future__ import annotations
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor,as_completed
from threading import Event
from time import perf_counter
import statistics,httpx
PROFILES={"Smoke":(1,5),"Normal":(5,20),"Load":(20,100),"Stress":(50,200),"Spike":(100,100),"Endurance":(10,500)}
@dataclass(frozen=True)
class LoadSummary: requests:int; successes:int; failures:int; rps:float; average_ms:float; p50_ms:float; p95_ms:float; p99_ms:float; error_rate:float
def run_load(url:str|list[str],users:int=5,requests:int=20,cancel:Event|None=None)->LoadSummary:
    cancel=cancel or Event(); times=[];successes=0
    targets=[url] if isinstance(url,str) else url
    if not targets: return LoadSummary(0,0,0,0,0,0,0,0,0)
    # A client is deliberately owned by each virtual user. Sharing one client
    # across concurrent worker threads can serialize local HTTP/1.1 traffic and
    # produce artificial multi-second tail latency.
    workers=max(1,min(users,requests))
    def worker(worker_index):
        results=[]
        with httpx.Client(timeout=10,trust_env=False) as client:
            # Warm each worker's connections. Warm-up responses are excluded.
            for target in targets:
                if cancel.is_set(): return results
                try: client.get(target)
                except httpx.HTTPError: pass
            for index in range(worker_index,requests,workers):
                if cancel.is_set(): break
                target=targets[index%len(targets)]; at=perf_counter()
                try: results.append((client.get(target).is_success,(perf_counter()-at)*1000))
                except httpx.HTTPError: results.append((False,(perf_counter()-at)*1000))
        return results
    started=perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(worker,index) for index in range(workers)]
        for future in as_completed(futures):
            for ok,elapsed in future.result(): successes+=ok;times.append(elapsed)
    total=len(times);quantile=lambda p:statistics.quantiles(times,n=100)[int(p)-1] if len(times)>=2 else (times[0] if times else 0)
    return LoadSummary(total,successes,total-successes,round(total/(perf_counter()-started),2) if total else 0,round(statistics.mean(times),1) if times else 0,round(quantile(50),1),round(quantile(95),1),round(quantile(99),1),round((total-successes)/total*100,2) if total else 0)
