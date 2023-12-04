import sys

from src.nnenum import nnenum_file

if __name__ == '__main__':
    # sys.argv.append("examples/acasxu/data/ACASXU_run2a_3_3_batch_2000.onnx")
    # sys.argv.append("examples/acasxu/data/prop_9.vnnlib")

    sys.argv.append(
        "examples/mnistfc/0.9217812418937683_f1Score__8_Epoch__2023_11_21_17_37_24_options.json_Options.onnx")
    sys.argv.append("examples/mnistfc/vnncomp2022_benchmarks/prop_0_0.03.vnnlib")
    #sys.argv.append("C:\\Code\\KIT\\vnncomp2022_benchmarks\\benchmarks\\mnist_fc\\vnnlib\\prop_0_0.03.vnnlib")

    nnenum_file.main()