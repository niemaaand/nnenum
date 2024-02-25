import copy
import csv
import json
import os
import sys
from enum import Enum

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from src.nnenum import nnenum_file
from src.nnenum.result import Result


class VerificationInstance:
    def __init__(self, big_onnx, small_onnx, vnnlib, timeout):
        self.big_onnx = big_onnx
        self.small_onnx = small_onnx
        self.vnnlib = vnnlib
        self.timeout = timeout


def _build_instance(path, network_type, row, small_net):
    return VerificationInstance(os.path.join(path, network_type, row[0]),  # onnx
                                os.path.join(path, network_type, small_net),  # small onnx
                                os.path.join(path, network_type, row[1]),  # vnnlib
                                row[2])  # timeout


def get_all_instances(path):
    instances = []

    for network_type in os.listdir(path):

        smaller_networks_file_path = os.path.join(path, network_type, "smaller_networks.json")
        with open(smaller_networks_file_path) as smaller_networks_file:
            smaller_networks_dict = json.load(smaller_networks_file)

        instances_file_path = os.path.join(path, network_type, "instances.csv")
        with open(instances_file_path) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=",")
            for row in csv_reader:

                small_net = ""
                if row[0] in smaller_networks_dict:
                    if smaller_networks_dict[row[0]]:
                        small_net = smaller_networks_dict[row[0]]

                instances.append(_build_instance(path, network_type, row, small_net))

    return instances


class CSVResultBuilder:

    class Rows(Enum):
        BIG_ONNX = "big onnx"
        SMALL_ONNX = "small onnx"
        VNNLIB = "vnnlib"
        DURATION_BIG_ONLY = "duration (big only)"
        DURATION_SMALL_AND_BIG = "duration (small and big)"
        DURATION_SMALL_ONLY = "duration (small only (included in small and big))"
        CLASSIFICATION_BIG = "classification (big only)"
        CLASSIFICATION_SMALL_AND_BIG = "classification (small and big)"
        N_SPLITS_BIG_ONLY = "number of splits (big only)"
        N_SPLITS_SMALL_AND_BIG = "number of splits (small and big)"
        FALSIFICATION_BY_COUNTEREXAMPLE = "falsification by counterexample"

    @staticmethod
    def build_csv_row(instance, result_big, result_small_and_big):
        return [instance.big_onnx, instance.small_onnx, instance.vnnlib,
                result_big.total_secs, result_small_and_big.total_secs if result_small_and_big else "", result_small_and_big.small_only_secs if result_small_and_big else "",
                result_big.result_str, result_small_and_big.result_str if result_small_and_big else "",
                result_big.n_split_fractions, result_small_and_big.n_split_fractions if result_small_and_big else "",
                result_small_and_big.big_network_proven_wrong.value]

    @staticmethod
    def build_headings():
        Rows = CSVResultBuilder.Rows
        return [Rows.BIG_ONNX.value, Rows.SMALL_ONNX.value, Rows.VNNLIB.value,
                Rows.DURATION_BIG_ONLY.value, Rows.DURATION_SMALL_AND_BIG.value, Rows.DURATION_SMALL_ONLY,
                Rows.CLASSIFICATION_BIG.value, Rows.CLASSIFICATION_SMALL_AND_BIG.value,
                Rows.N_SPLITS_BIG_ONLY.value, Rows.N_SPLITS_SMALL_AND_BIG.value,
                Rows.FALSIFICATION_BY_COUNTEREXAMPLE.value]

    @staticmethod
    def get_duration_big_only(row):
        return float(row[3])

    @staticmethod
    def get_duration_combined(row):
        return float(row[4])

    @staticmethod
    def get_duration_small_only(row):
        return float(row[5])

    @staticmethod
    def get_classification_big_only(row):
        return row[6]

    @staticmethod
    def get_classification_combined(row):
        return row[7]

    @staticmethod
    def get_n_splits_big_only(row):
        return row[8]

    @staticmethod
    def get_n_splits_combined(row):
        return row[9]

    @staticmethod
    def get_falsification_by_counter_example(row):
        return bool(int(row[10]))


def run_enumerations(benchmark_path, res_file_path):
    instances = get_all_instances(benchmark_path)
    results = []

    assert len(sys.argv) == 1
    prev = sys.argv[0]

    with open(res_file_path, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile, delimiter=",")
        csv_writer.writerow(CSVResultBuilder.build_headings())

    first_run = True  # warm up system
    instances.insert(0, copy.deepcopy(instances[0]))

    for instance in instances:

        result_big_onnx: Result = None
        result_small_and_big_onnx: Result = None

        for cnt in range(2 if instance.small_onnx else 1):

            sys.argv = []
            sys.argv.append(prev)

            if cnt == 0:
                # big onnx only
                sys.argv.append(instance.big_onnx)
                sys.argv.append("")
            elif cnt == 1:
                # small and big onnx
                sys.argv.append(instance.small_onnx)
                sys.argv.append(instance.big_onnx)
            else:
                raise NotImplementedError()

            sys.argv.append(instance.vnnlib)
            sys.argv.append(instance.timeout)

            if cnt == 0:
                # big onnx only
                result_big_onnx = nnenum_file.main()
            elif cnt == 1:
                # small and big onnx
                result_small_and_big_onnx = nnenum_file.main()
            else:
                raise NotImplementedError()

        if not first_run:
            results.append((result_big_onnx, result_small_and_big_onnx))

            with open(res_file_path, "a", newline="") as outfile:
                csv_writer = csv.writer(outfile, delimiter=",")
                csv_writer.writerow(CSVResultBuilder.build_csv_row(instance, result_big_onnx, result_small_and_big_onnx))
        else:
            print("\n\nStarting verifications...\n\n")

        first_run = False


def evaluate(eval_path):
    successful_results = ["safe", "unsafe (unconfirmed)", "unsafe"]

    # calc speedups (in percent)
    relative_speedups = []

    with open(eval_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")

        for row in csv_reader:

            assert len(row) == 11

            big_only_successful = CSVResultBuilder.get_classification_big_only(row) in successful_results
            small_and_big_successful = CSVResultBuilder.get_classification_combined(row) in successful_results
            if big_only_successful or small_and_big_successful:
                if big_only_successful and small_and_big_successful:
                    if CSVResultBuilder.get_classification_big_only(row) != CSVResultBuilder.get_classification_combined(row):
                        print("Different classification results in row number: {}".format(csv_reader.line_num))

                dur_big_only = CSVResultBuilder.get_duration_big_only(row)
                dur_small_and_big = CSVResultBuilder.get_duration_combined(row)

                relative_speedups.append(float(dur_small_and_big) / float(dur_big_only))

    return relative_speedups


def create_plot(eval_path):

    dur_bigs = []
    dur_smalls = []
    dur_comb = []

    successful_results = ["safe", "unsafe (unconfirmed)", "unsafe"]

    first_row = True
    small_big_unsuccessful = []
    big_unsuccessful = []
    falsified_by_counterexample = []

    with open(eval_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")

        for row in csv_reader:

            if not first_row:

                assert len(row) == 11
                dur_small_only = CSVResultBuilder.get_duration_small_only(row)
                dur_big_only = CSVResultBuilder.get_duration_big_only(row)
                dur_small_and_big = CSVResultBuilder.get_duration_combined(row)

                dur_bigs.append(dur_big_only)
                dur_smalls.append(dur_small_only)
                dur_comb.append(dur_small_and_big)

                big_only_successful = CSVResultBuilder.get_classification_big_only(row) in successful_results
                small_and_big_successful = CSVResultBuilder.get_classification_combined(row) in successful_results
                if big_only_successful:
                    big_unsuccessful.append(False)
                else:
                    big_unsuccessful.append(True)

                if small_and_big_successful:
                    small_big_unsuccessful.append(False)
                else:
                    small_big_unsuccessful.append(True)

                falsified_by_counterexample.append(CSVResultBuilder.get_falsification_by_counter_example(row))
            else:
                first_row = False

        max_dur = max(dur_bigs + dur_comb)

        ticksx = range(2, len(dur_bigs) + 2)
        ticksx = [str(x) for x in ticksx]
        for cnt in range(len(big_unsuccessful)):
            if big_unsuccessful[cnt] and small_big_unsuccessful[cnt]:
                ticksx[cnt] += "b"
            elif big_unsuccessful[cnt]:
                ticksx[cnt] += "t"
            elif small_big_unsuccessful[cnt]:
                ticksx[cnt] += "s"

            if falsified_by_counterexample[cnt]:
                ticksx[cnt] += "c"

        ticksy = [x * 25 for x in range(0, int(max_dur / 25) + 1)]

        barWidth = 0.25
        fig = plt.subplots(figsize=(12, 8))

        br1 = np.arange(len(dur_bigs))
        br2 = [x + barWidth for x in br1]
        br3 = [x + barWidth for x in br2]

        plt.bar(br1, dur_bigs, color="r", width=barWidth, edgecolor="grey", label="teacher only")
        plt.bar(br2, dur_smalls, color="g", width=barWidth, edgecolor="grey", label="student only")
        plt.bar(br3, dur_comb, color="b", width=barWidth, edgecolor="grey", label="both")

        plt.xlabel('Verification instances', fontweight='bold', fontsize=15)
        plt.xticks(br1, ticksx)
        plt.ylabel('time in s', fontweight='bold', fontsize=15)
        plt.yticks(ticksy)
        plt.yscale('log')
        plt.title("durations and timeouts ({})".format(os.path.basename(eval_path)))

        plt.legend(loc=1)
        #plt.legend([], ["t: teacher timeout", "s: student timeout", "b: both timeout", "c: counter example"], loc=4)
        plt.text(0, ticksy[-1], "t: teacher timeout\ns: student timeout\nb: both timeout\nc: counter example",
                 fontweight='bold', backgroundcolor=matplotlib.colors.to_rgba('lightgrey', 0.8))
        plt.show()


def print_stats(relative_speedups):
    relative_speedups.sort()
    print("Speedups: {}".format(len([p for p in relative_speedups if p <= 1])))
    print("Average Speedups: {}".format(sum(relative_speedups) / len(relative_speedups)))
    print("Median Speedups: {}".format(relative_speedups[int(len(relative_speedups) / 2)]))
    print("Fastest Speedup: {}".format(relative_speedups[0]))

