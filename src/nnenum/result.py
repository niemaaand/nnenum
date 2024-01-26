'''Enumeration result object definition

This defines the object returned by enumerate_network
'''

import multiprocessing

from src.nnenum.util import Freezable

class Result(Freezable):
    'computation result object'

    manager = None # created on first init

    # possible result strings in result_str
    results = ["none", "error", "timeout", "safe", "unsafe (unconfirmed)", "unsafe"]

    def __init__(self, nn, quick=False):
        if Result.manager is None:
            Result.manager = multiprocessing.Manager()
        
        # result string, one of Result.results
        # can be safe/unsafe only if a spec is provided to verification problem
        # "unsafe (unconfirmed)" means that the output set appeared to violate the spec, but no concrete trace
        # could be found, which can happen due to numerical accuracy in LP solving and during network execution
        self.result_str = "none"

        # total verification time, in seconds
        self.total_secs = None

        # total number of times LP solver was called during enumeration (statistic)
        self.total_lps_enum = 0

        # total number of times LP solver was called during enumeration and verification / plotting (statistic)
        self.total_lps = 0

        # total number of stars explored during path enumeration
        self.total_stars = 0

        # data (3-tuple) about problem progress: (finished_stars, unfinished_stars, finished_work_frac)
        self.progress_tuple = (0, 0, 0)

        ##### assigned if cls.RESULT_SAVE_TIMERS is nonempty. Map of timer_name -> total_seconds
        self.timers = {}

        self.n_split_fractions = 0

        self._nn = nn
        self.coutput_array = list()
        self.cinput_array = list()
        self.counterexample_oberservers = list()
        self.big_network_proven_wrong = multiprocessing.Value('i', 0) # TODO: stop if True

        if not quick:
            ###### assigned if Settings.RESULT_SAVE_POLYS = True. Each entry is polygon (list of 2-d points), ######
            self.polys = Result.manager.list()

            ###### assigned if Settings.RESULT_SAVE_STARS = True. Each entry is an LpStar ######
            self.stars = Result.manager.list()

            ###### below are assigned used if spec is not None and property is unsafe ######
            # counter-example boolean flags
            self.found_counterexample = multiprocessing.Value('i', 0)
            self.found_confirmed_counterexample = multiprocessing.Value('i', 0) # found counter-example with concrete input

            # concrete counter-example input and output
            self.coutput = multiprocessing.Array('d', nn.get_num_outputs())
            self.cinput = multiprocessing.Array('d', nn.get_num_inputs())
        else:
            # types may be different hmmm...
            self.polys = None
            self.stars = None
            self.found_counterexample = 0
            self.found_confirmed_counterexample = 0
            self.cinput = None
            self.coutput = None

        self.freeze_attrs()

    def get_new_cinput(self):
        return multiprocessing.Array('d', self._nn.get_num_inputs())

    def get_new_coutput(self):
        return multiprocessing.Array('d', self._nn.get_num_outputs())

    def add_counterexample(self, cinput, coutput):
        self.cinput_array.append(cinput)
        self.cinput = cinput
        self.coutput_array.append(coutput)
        self.coutput = coutput

        for co in self.counterexample_oberservers:
            co(cinput, coutput)


