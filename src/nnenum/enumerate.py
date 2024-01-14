'''
Stanley Bak

Enmeration functions for Neural Network Analysis

the method you probably want to use is enumerate_network()
'''

import multiprocessing
import time
import queue
import traceback

import numpy as np
import swiglpk as glpk

from src.nnenum.timerutil import Timers
from src.nnenum.lp_star import LpStar
from src.nnenum.lp_star_state import LpStarState
from src.nnenum.util import Freezable, FakeQueue, to_time_str, check_openblas_threads
from src.nnenum.settings import Settings
from src.nnenum.result import Result
from src.nnenum.network import NeuralNetwork, ReluLayer
from src.nnenum.worker import Worker
from src.nnenum.overapprox import try_quick_overapprox

from src.nnenum.prefilter import LpCanceledException

def make_init_ss(init, network, spec, start_time):
    'make the initial star state'

    network_inputs = network.get_num_inputs()
    network_outputs = network.get_num_outputs()

    if spec is not None:
        assert network_outputs == spec.get_num_expected_variables(), \
            f"spec expected {spec.get_num_expected_variables()} outputs; network had {network_outputs} outputs"

    if isinstance(init, (list, tuple, np.ndarray)):
        init_box = init

        assert len(init_box) == network_inputs, f"expected {network_inputs} dim init box, got {len(init_box)}"

        ss = LpStarState(init_box, spec=spec)
    elif isinstance(init, LpStar):
        ss = LpStarState(spec=spec)
        ss.from_init_star(init)
    else:
        assert isinstance(init, LpStarState), f"unsupported init type: {type(init)}"
        ss = init

    if ss.star.init_bias is not None:
        assert len(ss.star.init_bias) == network_inputs, f"init_bias len: {len(ss.star.init_bias)}" + \
            f", network inputs: {network_inputs}"

    ss.should_try_overapprox = False

    # propagate the initial star up to the first split
    timer_name = Timers.stack[-1].name if Timers.stack else None

    try: # catch lp timeout
        Timers.tic('propagate_up_to_split')
        ss.propagate_up_to_split(network, start_time)
        Timers.toc('propagate_up_to_split')
    except LpCanceledException:
        while Timers.stack and Timers.stack[-1].name != timer_name:
            Timers.toc(Timers.stack[-1].name)

        ss = None

    return ss

def enumerate_network(init, network, spec=None, network_big=None, use_multithreading=True, find_all_splits=False, reset_timers=True):
    '''enumerate the branches in the network

    init can either be a 2-d list or an lp_star or an lp_star_state

    settings are controlled by assigning directly to the class Settings, for example "Settings.timeout = 10"
    if spec is not None, a verification problem will be considered for the provided Specification object

    the output is an instance of Result
    '''

    assert Settings.TIMEOUT is not None, "use Settings.TIMEOUT = np.inf for no timeout"
    assert Settings.OVERAPPROX_LP_TIMEOUT is not None, "use Settings.OVERAPPROX_LP_TIMEOUT = np.inf for no timeout"

    if Settings.CHECK_SINGLE_THREAD_BLAS:
        check_openblas_threads()

    if reset_timers:
        Timers.reset()

    if not Settings.TIMING_STATS:
        Timers.disable()
    
    Timers.tic('enumerate_network')
    start = time.perf_counter()

    if Settings.BRANCH_MODE != Settings.BRANCH_EXACT:
        assert spec is not None, "spec required for overapproximation analysis"

    if not Settings.EAGER_BOUNDS:
        assert Settings.SPLIT_ORDER == Settings.SPLIT_INORDER

    assert not Settings.RESULT_SAVE_TIMERS or Settings.TIMING_STATS, \
        "RESULT_SAVE_TIMERS cannot be used if TIMING_STATS is False"

    init_ss = None
    concrete_io_tuple = None
    
    if time.perf_counter() - start < Settings.TIMEOUT:
        init_ss = make_init_ss(init, network, spec, start) # returns None if timeout

        proven_safe = False
        try_quick = Settings.TRY_QUICK_OVERAPPROX or Settings.SINGLE_SET

        if init_ss is not None and try_quick and spec is not None:
            #(proven_safe, concrete_io_tuple), violation_stars = try_quick_overapprox(init_ss, network, spec, start)
            proven_safe, concrete_io_tuple = try_quick_overapprox(init_ss, network, spec, start)

    if concrete_io_tuple is not None:
        # try_quick_overapprox found error
        if Settings.PRINT_OUTPUT:
            print("Proven unsafe before enumerate")
                
        rv = Result(network, quick=True)
        rv.result_str = 'unsafe'

        rv.cinput = concrete_io_tuple[0]
        rv.coutput = concrete_io_tuple[1]
    elif init_ss is None or time.perf_counter() - start > Settings.TIMEOUT:
        if Settings.PRINT_OUTPUT:
            print(f"Timeout before enumerate, init_ss is None: {init_ss is None}")
            
        rv = Result(network, quick=True)
        rv.result_str = 'timeout'
    elif proven_safe:
        if Settings.PRINT_OUTPUT:
            print("Proven safe before enumerate")
            
        rv = Result(network, quick=True)
        rv.result_str = 'safe'
    else:
        if Settings.SINGLE_SET:
            if Settings.PRINT_OUTPUT:
                print("SINGLE_SET analysis inconclusive.")
                
            rv = Result(network, quick=True)
            rv.result_str = 'none'
        else:
            if not use_multithreading:
                Settings.NUM_PROCESSES = 1

            num_workers = 1 if Settings.NUM_PROCESSES < 1 else Settings.NUM_PROCESSES

            shared = SharedState(network, spec, num_workers, start, find_all_splits)
            shared.push_init(init_ss)

            if shared.result.result_str != 'safe': # easy specs can be proven safe in push_init()
                Timers.tic('run workers')

                if num_workers == 1:
                    if Settings.PRINT_OUTPUT:
                        print("Running single-threaded")

                    worker_func(0, shared)
                else:
                    processes = []

                    if Settings.PRINT_OUTPUT:
                        print(f"Running in parallel with {num_workers} processes")

                    for index in range(Settings.NUM_PROCESSES):
                        p = multiprocessing.Process(target=worker_func, args=(index, shared))
                        p.start()
                        processes.append(p)

                    for p in processes:
                        p.join()

                Timers.toc('run workers')

            assert shared.more_work_queue.empty()

            shared.result.total_secs = time.perf_counter() - start

            if network_big:

                assert len(shared.done_work_list) > 0

                print("{} splits".format(len(shared.done_work_list)))
                #print("all splits: {}".format(shared.done_work_list))

                # deserialize
                for ss in shared.done_work_list:
                    if isinstance(ss.star.lpi.lp, tuple):
                        ss.star.lpi.deserialize()

                # there might remain some splits, because sub-network has already been proven save without performing split
                # move star to last layer of network
                for ss in shared.done_work_list:
                    if ss.remaining_splits() > 0:
                        n_layer = ss.cur_layer
                        while n_layer < len(shared.network.layers):
                            if not isinstance(shared.network.layers[n_layer], ReluLayer):
                                shared.network.layers[n_layer].transform_star(ss.star)
                            n_layer += 1
                    # else: do nothing

                # move stars to first layer of network
                assert isinstance(init, (list, tuple, np.ndarray))
                all_splits_first_layer = []
                for ss in shared.done_work_list:
                    ss_new = LpStarState(init, spec=shared.spec)
                    ss_new.prefilter = ss.prefilter
                    ss_new.star.input_bounds_witnesses = ss.star.input_bounds_witnesses
                    ss_new.star.lpi = ss.star.lpi
                    all_splits_first_layer.append(ss_new)
                    pass

                print("\nVerifying big network...\n")
                Timers.tic("verify_another_network")
                results_of_big_network = verify_another_network(network_big, all_splits_first_layer, shared.spec)
                Timers.toc("verify_another_network")
                print("\nVerification of big network done.\n")

                print("\nResult of small network:")
                process_result(shared)

                print("\nOverall result (big and small network): \n")
                overall_result: Result = results_of_big_network[-1]

                new_overall_result = Result(network_big)

                new_overall_result.total_secs = time.perf_counter() - start
                new_overall_result.timers = shared.result.timers

                new_overall_result.cinput = overall_result.cinput
                new_overall_result.coutput = overall_result.coutput
                new_overall_result.found_confirmed_counterexample = overall_result.found_confirmed_counterexample
                new_overall_result.found_counterexample = overall_result.found_counterexample
                new_overall_result.manager = overall_result.manager
                new_overall_result.result_str = overall_result.result_str

                new_finished_stars, new_unfinished_stars, new_finished_work_frac = (0, 0, 0)

                for r, cnt in zip(results_of_big_network, range(len(results_of_big_network))):
                    new_overall_result.polys += r.polys if r.polys else []
                    new_overall_result.stars += r.stars if r.stars else []
                    new_overall_result.total_lps += r.total_lps
                    new_overall_result.total_lps_enum += r.total_lps_enum
                    new_overall_result.total_stars += r.total_stars

                    (finished_stars, unfinished_stars, finished_work_frac) = r.progress_tuple
                    new_finished_stars += finished_stars
                    new_unfinished_stars += unfinished_stars
                    new_finished_work_frac += (finished_work_frac if cnt == len(results_of_big_network) - 1 else 1) * shared.done_work_list[cnt].work_frac

                new_overall_result.progress_tuple = (new_finished_stars, new_unfinished_stars, new_finished_work_frac)

                process_result_res(new_overall_result)

                rv = new_overall_result
            else:
                process_result(shared)
                rv = shared.result

    if rv.total_secs is None:
        rv.total_secs = time.perf_counter() - start

    Timers.toc('enumerate_network')

    if Settings.TIMING_STATS and Settings.PRINT_OUTPUT and rv.result_str != 'error' and reset_timers:
        Timers.print_stats()

    return rv


def process_result_res(result: Result):
    (finished_stars, unfinished_stars, finished_work_frac) = result.progress_tuple

    suffix = "" if result.total_secs < 60 else f" ({round(result.total_secs, 2)} sec)"
    print(f"Runtime: {to_time_str(result.total_secs)}{suffix}")
    print(f"Completed work frac: {finished_work_frac}")
    print(f"Num Lps During Enumeration: {result.total_lps_enum}")
    # count = shared.incorrect_overapprox_count.value
    # t = round(shared.incorrect_overapprox_time.value, 3)
    # print(f"Incorrect Overapproximation Time: {round(t/1000, 1)} sec (count: {count})")
    print(f"Total Num Lps: {result.total_lps}")
    print("")

    if result.result_str == "timeout":
        print(f"Timeout ({Settings.TIMEOUT}) reached during execution")
    elif result.found_confirmed_counterexample.value:
        print(f"Result: network is UNSAFE with confirmed counterexample in result.cinput and result.coutput")
        if len(result.cinput) <= 10:
            print(f"Input: {list(result.cinput)}")

        if len(result.coutput) <= 10:
            print(f"Output: {list(result.coutput)}")
    elif result.found_counterexample.value:
        print(f"Result: network seems UNSAFE, but not confirmed counterexamples (possible numerial " + \
              "precision issues)")
        # TODO: gradient descent -> adverserial attack to find counterexample
    else:
        print(f"Result: network is SAFE")  # safe subject to numerical accuracy issues

    if result.polys:
        print(f"Result contains {len(result.polys)} sets of polygons")

    enum_ended_early = result.result_str not in ["none", "safe"]

    if enum_ended_early and result.polys:
        print(f"Warning: result polygons / stars is incomplete, since the enumeration ended early")


def process_result(shared):
    'process a verification result'

    # save timing information
    if shared.had_exception.value:
        shared.result.result_str = "error"
    elif shared.had_timeout.value == 1:
        shared.result.result_str = "timeout"
    elif shared.result.found_confirmed_counterexample.value:
        shared.result.result_str = "unsafe"
    elif shared.result.found_counterexample.value:
        shared.result.result_str = "unsafe (unconfirmed)"
    elif shared.spec is not None:
        shared.result.result_str = "safe"

    # save num lps to result
    shared.result.total_lps = shared.num_lps.value

    # save num lps enum to result
    shared.result.total_lps_enum = shared.num_lps_enum.value

    # save num stars to result
    shared.result.total_stars = shared.finished_stars.value

    # save progress to result
    shared.result.progress_tuple = (shared.finished_stars.value,
                                    shared.unfinished_stars.value,
                                    shared.finished_work_frac.value)

    if Settings.PRINT_OUTPUT:
        if shared.had_exception.value == 1:
            print("Exception occured during execution")
        else:
            stars = shared.finished_stars.value
            approx = shared.finished_approx_stars.value
            print(f"\nTotal Stars: {stars} ({stars - approx} exact, {approx} approx)")

            if shared.spec is not None:
                print(f"Num Stars Copied Between Processes: {shared.num_offloaded.value}")
                process_result_res(shared.result)

    # if unsafe, convert concrete inputs / outputs to regular lists
    shared.result.cinput = list(shared.result.cinput)
    shared.result.coutput = list(shared.result.coutput)

    # deserialize stars if saved
    if shared.result.stars:
        shared.result.stars = list(shared.result.stars) # convert to normal list

        Timers.tic('deserialize result stars')

        for s in shared.result.stars:
            s.lpi.deserialize()

        Timers.toc('deserialize result stars')

    # save timers if requested
    for timer_name, count, secs in zip(Settings.RESULT_SAVE_TIMERS, shared.timer_counts, shared.timer_secs):
        shared.result.timers[timer_name] = (count, secs)


class SharedState(Freezable):
    'shared computation state across processes'

    def __init__(self, network, spec, num_workers, start_time, find_all_splits=False):
        assert isinstance(network, NeuralNetwork)
        
        # process-local copies
        self.network = network
        self.spec = spec
        self.num_workers = num_workers
        self.multithreaded = num_workers > 1
        self.find_all_splits = find_all_splits

        self.start_time = start_time

        # master -> worker
        # this lock should be used whenever modifying shared variables or consistency is needed,
        # except for the more_work_queue since that manages its own locks
        self.mutex = multiprocessing.Lock()
        self.done_work_list = list()

        if self.multithreaded:
            self.more_work_queue = multiprocessing.Queue()
        else:
            self.more_work_queue = FakeQueue() # use deque for single-threaded, faster

        # queue size is unreliable since multithreaded, use this instead
        self.stars_in_progress = multiprocessing.Value('i', 0)

        # used for load balancing
        self.heap_sizes = multiprocessing.Array('i', num_workers)

        # statistics worker -> master
        self.num_lps = multiprocessing.Value('i', 0)
        self.num_lps_enum = multiprocessing.Value('i', 0)
        self.num_offloaded = multiprocessing.Value('i', 0)
        self.finished_stars = multiprocessing.Value('i', 0)
        self.unfinished_stars = multiprocessing.Value('i', 0)
        
        self.finished_approx_stars = multiprocessing.Value('i', 0)
        self.finished_work_frac = multiprocessing.Value('f', 0) 
        self.incorrect_overapprox_count = multiprocessing.Value('i', 0)
        self.incorrect_overapprox_time = multiprocessing.Value('f', 0)

        num_timers = len(Settings.RESULT_SAVE_TIMERS)
        self.timer_secs = multiprocessing.Array('f', num_timers) # seconds, in same order as timers in Settings
        self.timer_counts = multiprocessing.Array('i', num_timers)

        self.cur_layers = multiprocessing.Array('i', num_workers)
        self.cur_neurons = multiprocessing.Array('i', num_workers)

        # status update if worker 0 finishes initial overapprox
        self.finished_initial_overapprox = multiprocessing.Value('i', 0)

        # set if an exception occurs so everyone exits
        self.had_exception = multiprocessing.Value('i', 0)

        # set if a timeout occured so everyone exits
        self.had_timeout = multiprocessing.Value('i', 0)

        # general flag if we should exit
        self.should_exit = multiprocessing.Value('i', 0)

        # result data
        self.result = Result(network)

        self.freeze_attrs()

    def push_init(self, ss):
        'put the initial init box or star onto the work queue'

        Timers.tic('push_init')

        # without the mutex here, if the threads start quickly, they may exit before finding the first piece of work
        # since the queue can be asynchronous
        ##############################
        self.mutex.acquire()
        self.put_queue(ss)
        self.stars_in_progress.value = 1
        self.mutex.release()
        ##############################

        Timers.toc('push_init')

    def put_queue(self, ss):
        'put a starstate on the queue'

        Timers.tic('put_queue')

        if self.multithreaded:
            ss.star.lpi.serialize()

        self.more_work_queue.put(ss)

        Timers.toc('put_queue')    

    def get_global_queue(self, block=True, timeout=None, skip_deserialize=False):
        '''pop a starstate from the global queue

        returns None on timeout
        '''

        Timers.tic('get_global_queue')

        try:
            rv = self.more_work_queue.get(block=block, timeout=timeout)

            if self.multithreaded and not skip_deserialize:
                rv.star.lpi.deserialize()

        except queue.Empty:
            rv = None

        Timers.toc('get_global_queue')

        return rv

class PrivateState(Freezable):
    'private state for work processes'

    def __init__(self, worker_index):
        self.worker_index = worker_index

        # ss is the current StarState being computed
        self.ss = None # pylint: disable=invalid-name
        #self.work_list = [] # list of tuples: (layer, neuron, id(ss), ss)

        self.work_list = []
        self.work_done_list = []

        self.branch_tuples_list = None # for saving of branch strs to file

        if self.worker_index == 0 and \
              (Settings.SAVE_BRANCH_TUPLES_FILENAME is not None or Settings.PRINT_BRANCH_TUPLES):
            self.branch_tuples_list = []
        
        self.total_overapprox_ms = 0
        self.max_approx_gen = 0

        # local copies of statistics
        self.finished_stars = 0
        self.finished_approx_stars = 0
        self.num_offloaded = 0
        self.num_lps = 0
        self.num_lps_enum = 0
        self.incorrect_overapprox_count = 0
        self.incorrect_overapprox_time = 0

        self.stars_in_progress = 0

        if Settings.SHUFFLE_TIME is not None:
            self.next_shuffle_step = Settings.SHUFFLE_TIME
            self.next_shuffle_time = time.time() + self.next_shuffle_step

        # shared variable timing updates
        self.next_shared_var_update = time.time() + Settings.UPDATE_SHARED_VARS_INTERVAL
        self.shared_update_urgent = False # used when work is popped to make sure we update heap sizes

        # fullfullment time stats
        self.fulfillment_requested_time = None
        self.total_fulfillment_time = 0
        self.total_fulfillment_count = 0

        # for updating shared stats
        self.update_stars = 0
        self.update_work_frac = 0.0
        self.update_stars_in_progress = 0

        # stats recorded by worker 0
        self.start_time = time.time()
        self.next_stats_time = self.start_time
        # stats is a list of timestamps, each timestamp is tuple (time, [stars_0, stars_1, ... stars_n])
        self.stats = []

        # used by worker 0 for periodic printing
        self.start_time = None
        self.last_print_time = None
        self.num_prints = 0

        # was there an exception (in another process)
        self.had_exception = 0

        self.freeze_attrs()


def verify_another_network(network, star_states, spec):
    res = []

    for star_state, cnt in zip(star_states, range(len(star_states))):

        print("\n\n{}th star: ".format(cnt))

        if isinstance(star_state.star.lpi.lp, tuple):
            star_state.star.lpi.deserialize()

        assert isinstance(star_state.star.lpi.lp, type(glpk.glp_create_prob())), "lp has to be type SwigPyObject"
        r_t = enumerate_network(star_state.star, network, spec, network_big=None,
                                use_multithreading=Settings.multithreading_big, find_all_splits=False,
                                reset_timers=False)
        res.append(r_t)

        if r_t.result_str != "safe":
            break

    return res


def worker_func(worker_index, shared):
    'worker function during verification'

    np.seterr(all='raise', under=Settings.UNDERFLOW_BEHAVIOR) # raise exceptions on floating-point errors

    if shared.multithreaded:
        Timers.stack.clear() # reset inherited Timers
        tag = f" (Process {worker_index})"
    else:
        tag = ""

    timer_name = f'worker_func{tag}'

    Timers.tic(timer_name)
    
    priv = PrivateState(worker_index)
    priv.start_time = shared.start_time
    w = Worker(shared, priv)

    try:
        #violation_stars, all_splits = w.main_loop()
        w.main_loop()

        if worker_index == 0 and Settings.PRINT_OUTPUT:
            print("\n")

            if Settings.SAVE_BRANCH_TUPLES_FILENAME is not None:
                with open(Settings.SAVE_BRANCH_TUPLES_FILENAME, 'w') as f:
                    for line in w.priv.branch_tuples_list:
                        f.write(f'{line}\n')

                    if not Settings.TIMING_STATS:
                        f.write(f"\nNo timing stats recorded because Settings.TIMING_STATS was False")
                    else:
                        f.write("\nStats:\n")

                        as_timer_list = Timers.top_level_timer.get_children_recursive('advance')
                        fs_timer_list = Timers.top_level_timer.get_children_recursive('finished_star')
                        to_timer_list = Timers.top_level_timer.get_children_recursive('do_overapprox_rounds')

                        if as_timer_list:
                            as_timer = as_timer_list[0]
                            exact_secs = as_timer.total_secs

                            if fs_timer_list:
                                exact_secs += fs_timer_list[0].total_secs
                        else:
                            exact_secs = 0

                        if to_timer_list:
                            to_timer = to_timer_list[0]
                            o_secs = to_timer.total_secs
                        else:
                            o_secs = 0

                        total_secs = exact_secs + o_secs

                        f.write(f"Total time: {round(total_secs, 3)} ({round(o_secs, 3)} overapprox, " + \
                                f"{round(exact_secs, 3)} exact)\n")

                        t = round(w.priv.total_overapprox_ms/1000, 3)
                        f.write(f"Sum total time for ONLY safe overapproxations (optimal): {t}\n")

        Timers.toc(timer_name)

        if shared.multithreaded and not shared.had_exception.value:
            if worker_index != 0 and Settings.PRINT_OUTPUT and Settings.TIMING_STATS:
                time.sleep(0.2) # delay to try to let worker 0 print timing stats first

            ##############################
            shared.mutex.acquire()
            # use mutex so printing doesn't get interrupted

            # computation time is sum of advance_star and finished_star
            if Settings.TIMING_STATS:
                as_timer_list = Timers.top_level_timer.get_children_recursive('advance')
                fs_timer_list = Timers.top_level_timer.get_children_recursive('finished_star')
                to_timer_list = Timers.top_level_timer.get_children_recursive('do_overapprox_rounds')

                as_secs = as_timer_list[0].total_secs if as_timer_list else 0
                fs_secs = fs_timer_list[0].total_secs if fs_timer_list else 0
                to_secs = to_timer_list[0].total_secs if to_timer_list else 0
                secs = as_secs + fs_secs

                exact_percent = 100 * secs / Timers.top_level_timer.total_secs
                over_percent = 100 * to_secs / Timers.top_level_timer.total_secs
                sum_percent = exact_percent + over_percent

                if Settings.PRINT_OUTPUT:
                    if w.priv.total_fulfillment_count > 0:
                        t = w.priv.total_fulfillment_time
                    else:
                        t = 0

                    e_stars = w.priv.finished_stars
                    a_stars = w.priv.finished_approx_stars
                    tot_stars = e_stars + a_stars
                    print(f"Worker {worker_index}: {tot_stars} stars ({e_stars} exact, {a_stars} approx); " + \
                          f"Working: {round(sum_percent, 1)}% (Exact: {round(exact_percent, 1)}%, " + \
                          f"Overapprox: {round(over_percent, 1)}%); " + \
                          f"Waiting: {round(1000*t, 3)}ms ")
            shared.mutex.release()
            ##############################

            if Settings.PRINT_OUTPUT and Settings.TIMING_STATS and \
               Settings.NUM_PROCESSES > 1 and worker_index == 0:
                time.sleep(0.4)
                print("")
                Timers.print_stats()
                print("")
    except Exception as e:
        if Settings.PRINT_OUTPUT:
            print("\n")
            traceback.print_exc()

        shared.mutex.acquire()
        shared.had_exception.value = True
        shared.should_exit.value = True
        shared.mutex.release()

        print(f"\nWorker {worker_index} had exception") 
        w.clear_remaining_work()

        # dump branch tuples
        if Settings.SAVE_BRANCH_TUPLES_FILENAME is not None:
            with open(Settings.SAVE_BRANCH_TUPLES_FILENAME, 'w') as f:
                for line in w.priv.branch_tuples_list:
                    f.write(f'{line}\n')

        # fix timers
        while Timers.stack and Timers.stack[-1].name != timer_name:
            Timers.toc(Timers.stack[-1].name)

        Timers.toc(timer_name)

