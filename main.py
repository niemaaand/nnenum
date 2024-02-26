import datetime
import os
import sys

from src.nnenum import nnenum_file
from src import evaluation

debug_network_onnx_path = "examples/debug/mini.onnx"
debug_network_big_onnx_path = "examples/debug/mini2BIG.onnx"
debug_network_vnnlib_path = "examples/debug/mini2.vnnlib"
benchmark_path = "vnncomp2022_benchmarks/benchmarks"


if __name__ == '__main__':

    #res_file_path = os.path.join("results", "{}_result_file.csv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
    res_file_path = "results/2024-02-04_18-10-00_result_file.csv"
    #evaluation.run_enumerations(benchmark_path, res_file_path)
    relative_speedups_unsafe = evaluation.evaluate(res_file_path, successful_results=["unsafe (unconfirmed)", "unsafe"])
    relative_speedups_safe = evaluation.evaluate(res_file_path, successful_results=["safe"])
    print("\nunsafe\n")
    evaluation.print_stats(relative_speedups_unsafe)
    print("\nsafe\n")
    evaluation.print_stats(relative_speedups_safe)
    #evaluation.create_plot(res_file_path)

    pass