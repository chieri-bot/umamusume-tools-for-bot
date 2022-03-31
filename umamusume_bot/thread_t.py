from threading import Thread
from typing import List
import time


none_symbol = "nonedesuyo"


class NewThread(Thread):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = none_symbol

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):
        return self.result


class ThreadTasks:
    def __init__(self):
        self.threads: List[NewThread] = []
        self.is_start = False

    def add_thread(self, func, *args, **kwargs):
        t = NewThread(func, *args, **kwargs)
        self.threads.append(t)

    def start(self):
        if self.is_start:
            return
        self.is_start = True
        for _t in self.threads:
            _t.start()

    def get_results(self, time_out=-1, ignore_none=True):
        if not self.is_start:
            self.start()
        t_s = time.time()
        result = [none_symbol] * len(self.threads)
        none_count = -1
        while none_count != 0:
            time_spend = time.time() - t_s
            # print(time_spend)
            if time_out != -1 and time_spend > time_out:
                return result
            count = 0
            for task in self.threads:
                if result[count] != none_symbol:
                    continue
                _r = task.get_result()
                if _r != none_symbol:
                    result[count] = _r
                count += 1
            none_count = result.count(none_symbol)
            # print(none_count)
            time.sleep(0.5)
        print("耗时", time.time() - t_s)
        if ignore_none:
            result = [i for i in result if i != none_symbol]
        return result
