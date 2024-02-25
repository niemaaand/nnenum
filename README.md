# General information
This repository extends nnenum (https://github.com/stanleybak/nnenum) to 
verifying not only a neural Network A, but also another network B (where B is intended 
to be smaller than A). The splits produced by verifying B are collected, transformed to 
input space and used to verify A. 

A benchmark for evaluation (vnncomp2022_benchmarks/benchmarks/mnist_fc 
from https://github.com/ChristopherBrix/vnncomp2022_benchmarks) has been 
added along with some smaller networks (vnncomp2022_benchmarks/benchmarks/mnist_fc/onnx_small). 

The mapping, which small network to use for which big network, is done by the file 
vnncomp2022_benchmarks/benchmarks/mnist_fc/smaller_networks.json with "big: small" ("key: value"). 

The smaller networks included in this repository were trained by student teacher training, the 
code can be found at https://github.com/niemaaand/PraktikumProgrammverifikation. 

The results of the evaluation are summarized in results/Evaluation.md. 


