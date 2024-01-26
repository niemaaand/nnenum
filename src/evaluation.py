import csv
import json
import os
import sys
from enum import Enum

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
        CLASSIFICATION_BIG = "classification (big only)"
        CLASSIFICATION_SMALL_AND_BIG = "classification (small and big)"
        N_SPLITS_BIG_ONLY = "number of splits (big only)"
        N_SPLITS_SMALL_AND_BIG = "number of splits (small and big)"
        FALSIFICATION_BY_COUNTEREXAMPLE = "falsification by counterexample"

    @staticmethod
    def build_csv_row(instance, result_big, result_small_and_big):
        return [instance.big_onnx, instance.small_onnx, instance.vnnlib,
                result_big.total_secs, result_small_and_big.total_secs if result_small_and_big else "",
                result_big.result_str, result_small_and_big.result_str if result_small_and_big else "",
                result_big.n_split_fractions, result_small_and_big.n_split_fractions if result_small_and_big else "",
                result_small_and_big.big_network_proven_wrong.value]

    @staticmethod
    def build_headings():
        Rows = CSVResultBuilder.Rows
        return [Rows.BIG_ONNX.value, Rows.SMALL_ONNX.value, Rows.VNNLIB.value,
                Rows.DURATION_BIG_ONLY.value, Rows.DURATION_SMALL_AND_BIG.value,
                Rows.CLASSIFICATION_BIG.value, Rows.CLASSIFICATION_SMALL_AND_BIG.value,
                Rows.N_SPLITS_BIG_ONLY.value, Rows.N_SPLITS_SMALL_AND_BIG.value,
                Rows.FALSIFICATION_BY_COUNTEREXAMPLE.value]

    @staticmethod
    def get_duration_big_only(row):
        return row[3]

    @staticmethod
    def get_duration_combined(row):
        return row[4]

    @staticmethod
    def get_classification_big_only(row):
        return row[5]

    @staticmethod
    def get_classification_combined(row):
        return row[6]


def run_enumerations(benchmark_path, res_file_path):
    instances = get_all_instances(benchmark_path)
    results = []

    assert len(sys.argv) == 1
    prev = sys.argv[0]

    with open(res_file_path, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile, delimiter=",")
        csv_writer.writerow(CSVResultBuilder.build_headings())

    first_run = True  # warm up system
    instances.insert(0, instances[0])

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

        first_run = False

def evaluate(eval_path):
    successful_results = ["safe", "unsafe (unconfirmed)", "unsafe"]

    # calc speedups (in percent)
    relative_speedups = []
    with open(eval_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")

        for row in csv_reader:
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
