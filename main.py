import sys

from src.nnenum import nnenum_file

if __name__ == '__main__':

    sys.argv.append("examples/acasxu/data/ACASXU_run2a_3_3_batch_2000.onnx")
    sys.argv.append("examples/acasxu/data/prop_9.vnnlib")

    nnenum_file.main()