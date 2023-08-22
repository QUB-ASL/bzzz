import bzzz.thread_this
from time import time_ns


class Scheduler:
    """Scheduler class can be used to schedule functions to be run at a particular
    rate. To proberly schedule and run functions follow the below steps:
    1. Create a `Scheduler` object. 
        1.1 By default the class checks the time elapsed since the 
            last call of a function to decide whether to run the function or not. The class
            keeps a seperate time record for each function scheduled. 
        1.2 You can select to use the threading class for this task instead of using the above logic.
        1.3 You only need a single `Scheduler` object to schedule multiple functions. You can also create 
            multiple `Scheduler` objects, but this is discouraged because:
                a. This generally serves no purpose as a single objects is capable of handling multiple functions.
                b. Having multiple objects with different functions scheduled can lead to confusion as to which object 
                    handels which set of functions.
                c. Having multiple objects does not gurantee that your program runs any faster, this stays true 
                    even when using the `threading` class. So, basically no potential advantage to performance at the 
                    expence of having multiple objects occupying memory.
    2. Use the `schedule` function to schedule a function. Each function should be scheduled by a seperate call of the
        `schedule` function.
        2.1 It is encouraged to group together all the `schedule` calls in one place and schedule all the required functions
            at the same point before running these functions.
            a. This keeps the code clean and avoids confusion.
            b. This can ensure that the run-times for each function scheduled to be **relatively** unchanged.
        2.2 You are allowed to schedule functions at any point in time and from anywhere with in the scope of the object, 
            but this is severely discouraged because of points 2.1.a and 2.1.b.
    3. You need to call the `run` function continuosly in a while loop if you are did not select for using the `threading` library.
    4. You can kill or unschedule a particular function using the `kill` function. You can kill a function at any desired time and
        from anywhere with in the scope of the object.
        4.1 It is recommended to kill all functions one by one before exiting the entire program.
    """
    # Dict keys
    _function_ID = "function_ID"
    _function_obj = "function_obj"
    _function_call_frequency = "function_call_frequency"
    _function_call_count = "function_call_count"
    _function_thread = "function_thread"
    _num_times_called = "num_times_called"
    _time_at_last_call_ns = "time_at_last_call_ns"
    _dummy_func = "dummy_func"

    def __init__(self, use_threading=False):
        """Constructor

        :param use_threading: Enable to use the `threading` library, defaults to False
        """
        # This variable is a dict with the following structure
        # {
        #   function_name: 
        #       {
        #           function_ID: int, function_obj: obj,
        #           function_call_frequency: Hz, function_call_count: int,
        #           function_thread: threading.Timer or None,
        #           num_times_called: int, time_at_last_call_ns: int
        #       }
        # }
        self.__functions_to_run = {}
        self.__last_function_ID = -1
        self.__use_threading = use_threading
        self.__scheduled_events = []

        # dummy function used as a place holder
        self.__functions_to_run[Scheduler._dummy_func] = {
            Scheduler._function_ID: self.__last_function_ID,
            Scheduler._function_obj: -1,
            Scheduler._function_call_frequency: -1,
            Scheduler._function_call_count: -1,
            Scheduler._function_thread: -1, 
            Scheduler._num_times_called: -1, 
            Scheduler._time_at_last_call_ns: -1
            }

    def schedule(self, function_name, function_obj, function_call_frequency, function_call_count=0):
        """Schedules a given function. This function should be called seperately to schedule different functions.

        :param function_name: Name of the function as a string.
        :param function_obj: The function object.
        :param function_call_frequency: The desired function call rate in Hz.
        :param function_call_count: (The life time of the function) Maximum number of times the function 
                can be called before it is unscheduled. Set this to  0 to run the function indefinetly, defaults to 0
        """
        self.__last_function_ID += 1
        f_thread = None
        if self.__use_threading:
            f_thread = bzzz.thread_this.run_thread_every_given_interval(
                interval=1./function_call_frequency, function_to_run=function_obj, num_times_to_run=function_call_count)
        self.__scheduled_events.append(function_name)
        self.__functions_to_run[function_name] = {
            Scheduler._function_ID: self.__last_function_ID, 
            Scheduler._function_obj: function_obj,
            Scheduler._function_call_frequency: function_call_frequency, 
            Scheduler._function_call_count: function_call_count,
            Scheduler._function_thread: f_thread, 
            Scheduler._num_times_called: 0, 
            Scheduler._time_at_last_call_ns: time_ns()
            }

    def function_ID(self, function_name):
        """Return the function's unique ID based on provided name.

        :param function_name: The function name in string to fetch ID.
        :return: returns the function's ID if scheduled, otherwise -1.
        """
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_ID)

    def function_obj(self, function_name):
        """Return the function's object based on provided name.

        :param function_name: The function name in string to fetch the object.
        :return: returns the function's object if scheduled, otherwise -1.
        """
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_obj)

    def function_call_frequency(self, function_name):
        """Return the function's call rate based on provided name.

        :param function_name: The function name in string to fetch the call rate.
        :return: returns the function's call rate if scheduled, otherwise -1.
        """
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_call_frequency)

    def function_call_count(self, function_name):
        """Return the function's call rate based on provided name.

        :param function_name: The function name in string to fetch the call rate.
        :return: returns the function's call rate if scheduled, otherwise -1.
        """
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_call_count)

    def function_thread(self, function_name):
        """Return the function's thread handle based on provided name.

        :param function_name: The function name in string to fetch its thread handle.
        :return: returns the function's thread handle if scheduled and selected to use threading, otherwise None.
        """
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._function_thread)

    def num_times_called(self, function_name, increment=False, change_value=False, to_value=1):
        """Return the function's call count based on provided name.

        :param function_name: The function name in string to fetch the call count.
        :return: returns the function's call count if scheduled, otherwise -1.
        """
        if function_name in self.__scheduled_events:
            if increment:
                self.__functions_to_run[function_name][Scheduler._num_times_called] += 1
            if change_value:
                self.__functions_to_run[function_name][Scheduler._num_times_called] = to_value

        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._num_times_called)

    def time_at_last_call_ns(self, function_name, change=False, to_value=0):
        """Return the function's last call time stamp based on provided name.

        :param function_name: The function name in string to fetch the last call time stamp.
        :return: returns the function's last call time stamp, otherwise -1.
        """
        if change and function_name in self.__scheduled_events:
            self.__functions_to_run[function_name][Scheduler._time_at_last_call_ns] = to_value
        return self.__functions_to_run.get(function_name, self.__functions_to_run[Scheduler._dummy_func]).get(Scheduler._time_at_last_call_ns)

    def run(self):
        """Check whether to run each function and run once if yes. 
            This runs through the scheduled functions only once.
            No need to call this function if the `threading` class in in use.
            You need to continuously call this function in a loop.
        """
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
        """Unschedule or kill based on provided name. You need to call this even 
            when threading class is in use. It is recommended to call this on all of
            the scheduled functions before exiting the entire program.

        :param function_name: The function name in string to unschedule.
        """
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
