import sys

from src.nnenum import nnenum_file


debug_network_onnx_path = "examples/debug/mini2.onnx"
debug_network_big_onnx_path = "examples/debug/mini2BIG.onnx"
debug_network_vnnlib_path = "examples/debug/mini2.vnnlib"


if __name__ == '__main__':
    sys.argv.append("examples/acasxu/data/ACASXU_run2a_3_3_batch_2000.onnx")
    sys.argv.append("")
    sys.argv.append("examples/acasxu/data/prop_9.vnnlib")

    #sys.argv.append("examples/mnistfc/0.9217812418937683_f1Score__8_Epoch__2023_11_21_17_37_24_options.json_Options.onnx")
    #sys.argv.append("vnncomp2022_benchmarks\\benchmarks\\mnist_fc\\onnx\\mnist-net_256x6.onnx")
    #sys.argv.append("")
    #sys.argv.append("examples/mnistfc/vnncomp2022_benchmarks/prop_1_0.05.vnnlib")
    #sys.argv.append("vnncomp2022_benchmarks\\benchmarks\\mnist_fc\\vnnlib\\prop_0_0.03.vnnlib") # C:\\Code\\KIT

    #sys.argv.append(debug_network_onnx_path)
    #sys.argv.append(debug_network_big_onnx_path)
    #sys.argv.append(debug_network_vnnlib_path)

    nnenum_file.main()
    pass