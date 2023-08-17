import threading

def run_thread_every_given_interval(interval,
                                    function_to_run,
                                    num_times_to_run=0):
    """
    Create a thread of the given function, attach a timer 
    to it and run it everytime the interval is elapsed.

    :param interval: Interval between each run in seconds. 
        Note: the given interval must be larger than worst 
        execution time of the given function.
    :param function_to_run: Function handle which is to be run.
    :param num_times_to_run: Number of times to run the thread before killing it
        0 means that the thread is called as long as the program doesn't 
        terminate, defaults to 0.
    """
    if num_times_to_run != 1:
        thread = threading.Timer(interval, run_thread_every_given_interval, [
                        interval, function_to_run, num_times_to_run if num_times_to_run else 0])
        thread.start()
    function_to_run()
    return thread
