import bzzz.thread_this
from time import time_ns


class Scheduler:
    # Dict keys
    _function_ID = "function_ID"
    _function_obj = "function_obj"
    _function_call_frequency = "function_call_frequency"
    _function_call_count = "function_call_count"
    _function_thread = "function_thread"
    _num_times_called = "num_times_called"
    _time_at_last_call_ns = "time_at_last_call_ns"
    _dummy_func = "dummy_func"

    def __init__(self, use_threading=False) -> None:
        # This variable is a dict with the following structure
        # {function_name: {function_ID: int, function_obj: obj, function_call_frequency: Hz, function_call_count: int, function_thread: threading.Timer or None, num_times_called: int, time_at_last_call_ns: int}}
        self.__functions_to_run = {}
        self.__last_function_ID = -1
        self.__use_threading = use_threading
        self.__scheduled_events = []

        self.__functions_to_run[Scheduler._dummy_func] = {
            Scheduler._function_ID: self.__last_function_ID, Scheduler._function_obj: -1,
            Scheduler._function_call_frequency: -1, Scheduler._function_call_count: -1,
            Scheduler._function_thread: -1, Scheduler._num_times_called: -1, Scheduler._time_at_last_call_ns: -1}

    def schedule(self, function_name: str, function_obj, function_call_frequency, function_call_count=0):
        self.__last_function_ID += 1
        f_thread = None
        if self.__use_threading:
            f_thread = bzzz.thread_this.run_thread_every_given_interval(
                interval=1./function_call_frequency, function_to_run=function_obj, num_times_to_run=function_call_count)
        self.__scheduled_events.append(function_name)
        self.__functions_to_run[function_name] = {
            Scheduler._function_ID: self.__last_function_ID, Scheduler._function_obj: function_obj,
            Scheduler._function_call_frequency: function_call_frequency, Scheduler._function_call_count: function_call_count,
            Scheduler._function_thread: f_thread, Scheduler._num_times_called: 0, Scheduler._time_at_last_call_ns: time_ns()}

    def function_ID(self, function_name):
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_ID)

    def function_obj(self, function_name):
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_obj)

    def function_call_frequency(self, function_name):
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_call_frequency)

    def function_call_count(self, function_name):
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_call_count)

    def function_thread(self, function_name):
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_thread)

    def num_times_called(self, function_name, increment=False, change_value=False, to_value=1):
        if function_name in self.__scheduled_events:
            if increment:
                self.__functions_to_run[function_name][Scheduler._num_times_called] += 1
            if change_value:
                self.__functions_to_run[function_name][Scheduler._num_times_called] = to_value

        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._num_times_called)

    def time_at_last_call_ns(self, function_name, change=False, to_value=0):
        if change and function_name in self.__scheduled_events:
            self.__functions_to_run[function_name][Scheduler._time_at_last_call_ns] = to_value
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._time_at_last_call_ns)

    def run(self):
        if not self.__use_threading:
            time_now = time_ns()
            for func in self.__functions_to_run:
                if func is not Scheduler._dummy_func:
                    if (time_now - self.time_at_last_call_ns(func))*1e-9 >= 1./self.function_call_frequency(func):
                        if self.num_times_called(func) <= self.function_call_count(func):
                            self.function_obj(func)()
                            self.num_times_called(func, increment=(
                                self.function_call_count(func) != 0))
                            self.time_at_last_call_ns(
                                func, change=True, to_value=time_now)

    def kill(self, function_name):
        print(f"Called kill on {function_name}")
        if function_name in self.__scheduled_events:
            if self.__use_threading:
                f_thread = self.function_thread(function_name)
                if f_thread != -1:
                    f_thread.cancel()
                    print(f"{function_name}: Function thread killed")
            else:
                self.num_times_called(
                    function_name, change_value=True, to_value=self.function_call_count(function_name))
        else:
            print(f"No function named {function_name} was scheduled.")
