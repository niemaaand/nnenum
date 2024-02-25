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

    res_file_path = os.path.join("results", "{}_result_file.csv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
    #res_file_path = "results/2024-02-04_17-20-15_result_file.csv"
    evaluation.run_enumerations(benchmark_path, res_file_path)
    relative_speedups = evaluation.evaluate(res_file_path)
    evaluation.create_plot(res_file_path)

    #eval_path = "results/2024-02-04_17-20-15_result_file.csv"
    #eval_path = res_file_path
    #relative_speedups = evaluation.evaluate(eval_path)
    evaluation.print_stats(relative_speedups)

    #"vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx/mnist-net_256x2.onnx"
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks\mnist_fc\onnx_small/2024_02_04_14_41_43_options.json_Options__0.855400025844574_f1Score__8_Epoch.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks\mnist_fc\onnx_small/2024_02_04_14_41_43_options.json_Options__0.855400025844574_f1Score__8_Epoch.onnx")
    #sys.argv.append("")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_14_0.05.vnnlib") # unsafe
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_6_0.03.vnnlib") # unsafe
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_5_0.03.vnnlib")


    # safe with 3 splits
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks\mnist_fc\onnx/mnist-net_256x2.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks\mnist_fc\onnx/mnist-net_256x2.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_8_0.03.vnnlib")

    pass

    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx_small/2024_02_05_17_57_24_options.json_Options__0.8366000056266785_f1Score__18_Epoch.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx/mnist-net_256x4.onnx")
    #sys.argv.append("")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_2_0.05.vnnlib")
    #sys.argv.append(300)

    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx_small/2024_01_27_17_55_09_options.json_Options__0.9793000221252441_f1Score__9_Epoch.onnx")
    #sys.argv.append("")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_4_0.03.vnnlib")

    #sys.argv.append("examples/acasxu/data/ACASXU_run2a_3_3_batch_2000.onnx")
    #sys.argv.append("")
    #sys.argv.append("examples/acasxu/data/prop_9.vnnlib")

    #sys.argv.append("examples/mnistfc/2024_01_13_15_47_33_options.json_Options__0.8756420612335205_f1Score__0_Epoch.onnx")
    #sys.argv.append("examples/mnistfc/0.9217812418937683_f1Score__8_Epoch__2023_11_21_17_37_24_options.json_Options.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx/mnist-net_256x4.onnx")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx/mnist-net_256x6.onnx")
    #sys.argv.append("")
    #sys.argv.append("examples/mnistfc/vnncomp2022_benchmarks/prop_1_0.05.vnnlib")
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_1_0.05.vnnlib") # C:\\Code\\KIT
    #sys.argv.append("vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_0_0.03.vnnlib")

    #sys.argv.append(debug_network_onnx_path)
    #sys.argv.append(debug_network_big_onnx_path)
    #sys.argv.append("")
    #sys.argv.append(debug_network_vnnlib_path)

    #res = nnenum_file.main()
    pass