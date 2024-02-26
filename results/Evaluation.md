# Student-Teacher-Training Evaluation

## Explanation
In one table, all options for training the models are the same. The models are trained independently. Each of the models is the best of its training period.  

Verification-tasks are only performed for the teacher-network under inspection. 

Only those verification-instances are considered for evaluation, where ate least one of the methods, BigOnly and SmallAndBig, has no timeout. 

If differences to multiple other chapters are given, this are alternative ways to reach to current options. 

Calculation of speedup per network: 
$speedup = \frac{verificationTimeOfSmallAndBigNetwork}{ verificationTimeOfBigNetwork}$ 

Therefor, $speedup < 1$ means actual speedup, $speedup > 1$ means the proposed method needed more time. 


## Mapping of chapters to elaboration
### Teacher: mnist-net_256x2.onnx
 - 16.96 -> Ch. 1
 - 31.42 -> Ch. 3
 - 14.06 -> Ch. 2
 - 1.7 -> Ch. 5
 - 11.07 -> Ch. 8
 - 47.82 -> Ch. 4
 - 36.98 -> Ch. 7
 - Training for single property -> Ch. 6

### Teacher: own
 - 2.05 -> Ch. 3


## mnist-net_256x2.onnx

F1-Score of Teacher: 0.9808

### 1
| Metric          | Student1                                                                            | Student2                                                                           | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_11_49_42_options.json_Options__0.9667999744415283_f1Score__18_Epoch.onnx | 2024_02_04_12_03_16_options.json_Options__0.9703999757766724_f1Score__8_Epoch.onnx | 2024_02_04_12_07_26_options.json_Options__0.9682999849319458_f1Score__17_Epoch.onnx |
| F1-Score        | 0.967                                                                               | 0.970                                                                              | 0.968                                                                               |
| Verification    | 2024-02-04_13-09-50_result_file.csv                                                 | 2024-02-04_19-46-24_result_file.csv                                                |                                                                                     |
| Speedups        | 0                                                                                   | 3                                                                                  |                                                                                     |
| Average Speedup | 60.17                                                                               | 46.34                                                                              |                                                                                     |
| Median Speedup  | 25.98                                                                               | 7.93                                                                               |                                                                                     |
| Fastest Speedup | 1.17                                                                                | 0.11                                                                               |                                                                                     |

### 2
Differences to 1: 
 - soft_target_loss_weight: from 0.25 to 0.0
 - ce_loss_weight: from 0.75 to 1.0
 - -> Therefore temperature-values are irrelevant, since tempereature is only used with soft_target_loss_weight > 0

| Metric          | Student1                                                                            | Student2                                                                          | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_12_38_28_options.json_Options__0.9664999842643738_f1Score__17_Epoch.onnx | 2024_02_04_12_42_55_options.json_Options__0.96670001745224_f1Score__16_Epoch.onnx | 2024_02_04_12_47_21_options.json_Options__0.9722999930381775_f1Score__12_Epoch.onnx |
| F1-Score        | 0.966                                                                               | 0.967                                                                             | 0.972                                                                               |
| Verification    | 2024-02-04_21-14-30_result_file.csv                                                 |                                                                                   | 2024-02-04_22-34-00_result_file.csv                                                 |
| Speedups        | 1                                                                                   |                                                                                   | 0                                                                                   |
| Average Speedup | 70.13                                                                               |                                                                                   | 70.60                                                                               |
| Median Speedup  | 14.72                                                                               |                                                                                   | 13.39                                                                               |
| Fastest Speedup | 0.98                                                                                |                                                                                   | 1.11                                                                                |

### 3
Differences to 1: 
 - criterion: from MSELoss to CrossEntropyLoss

| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                           |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| File            | 2024_02_04_13_58_16_options.json_Options__0.9822999835014343_f1Score__12_Epoch.onnx | 2024_02_04_14_03_47_options.json_Options__0.9817000031471252_f1Score__10_Epoch.onnx | 2024_02_04_14_08_18_options.json_Options__0.982699990272522_f1Score__16_Epoch.onnx |
| F1-Score        | 0.9822                                                                              | 0.9817                                                                              | 0.9827                                                                             |
| Verification    | 2024-02-04_18-36-58_result_file.csv                                                 |                                                                                     | 2024-02-04_15-53-01_result_file.csv                                                |
| Speedups        | 1                                                                                   |                                                                                     | 1                                                                                  |
| Average Speedup | 200.90                                                                              |                                                                                     | 234.78                                                                             |
| Median Speedup  | 26.39                                                                               |                                                                                     | 36.45                                                                              | 
| Fastest Speedup | 0.59                                                                                |                                                                                     | 0.54                                                                               |

### 4
Differences to 3:
 - choose_best_model_based_on_teacher: from False to True
    - Here the reference for F1-Score is NOT the labels, but the teachers predictions
    - This means, it can be assumed, that this model behaves more similar to its teacher model. 

| Metric          | Student1                                                                            | Student2                                                                          | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_14_13_43_options.json_Options__0.9835000038146973_f1Score__16_Epoch.onnx | 2024_02_04_14_18_29_options.json_Options__0.983299970626831_f1Score__9_Epoch.onnx | 2024_02_04_14_26_19_options.json_Options__0.9825999736785889_f1Score__14_Epoch.onnx |
| F1-Score        | 0.9835                                                                              | 0.9833                                                                            | 0.9826                                                                              |
| Verification    | 2024-02-05_08-14-06_result_file.csv                                                 |                                                                                   | 2024-02-05_09-20-41_result_file.csv                                                 |
| Speedups        | 2                                                                                   |                                                                                   | 1                                                                                   |
| Average Speedup | 210.01                                                                              |                                                                                   | 321.73                                                                              |
| Median Speedup  | 49.37                                                                               |                                                                                   | 46.27                                                                               |
| Fastest Speedup | 0.40                                                                                |                                                                                   | 0.36                                                                                |

### 5

Differences to 2:
 - criterion: from MSELoss to CrossEntropyLoss

Differences to 3:
 - soft_target_loss_weight: from 0.25 to 0.0
 - ce_loss_weight: from 0.75 to 1.0

| Metric          | Student1                                                                           | Student2                                                                          | Student3                                                                          |
|-----------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| File            | 2024_02_04_14_37_06_options.json_Options__0.8547999858856201_f1Score__2_Epoch.onnx | 2024_02_04_14_41_43_options.json_Options__0.855400025844574_f1Score__8_Epoch.onnx | 2024_02_04_14_46_43_options.json_Options__0.858299970626831_f1Score__4_Epoch.onnx |
| F1-Score        | 0.8548                                                                             | 0.8554                                                                            | 0.8583                                                                            |
| Verification    |                                                                                    | 2024-02-04_18-10-00_result_file.csv                                               | 2024-02-04_17-20-15_result_file.csv                                               |
| Speedups        |                                                                                    | 2                                                                                 | 2                                                                                 |
| Average Speedup |                                                                                    | 6.29                                                                              | 4.45                                                                              |
| Median Speedup  |                                                                                    | 1.67                                                                              | 1.73                                                                              | 
| Fastest Speedup |                                                                                    | 0.28                                                                              | 0.9                                                                               | 


### 6
#### Especially trained for this category - prop_0_0.03.vnnlib
Differences to 3:
 - vnnlibs_path: from "" to "vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_0_0.03.vnnlib"
 - dataset: from MNIST to RANDOM_INPUTS

Notice: Prediction (hard labels) are always the same, since this network has only been **trained for one property**. F1-Score on whole dataset therefore is bad - everything is classified as the same, which is correct in about 1/10 of the cases. 

**Verification-Speedup is only validated on the property, the network has been trained for!**

Therefor, the speedups here are not comparable to other speedups, because of high variance in the speedups verification-instance. 

| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_21_01_26_options.json_Options__0.09700000286102295_f1Score__0_Epoch.onnx | 2024_02_04_21_03_19_options.json_Options__0.09700000286102295_f1Score__0_Epoch.onnx | 2024_02_04_21_05_20_options.json_Options__0.09700000286102295_f1Score__0_Epoch.onnx |
| F1-Score        | 0.097                                                                               | 0.097                                                                               | 0.097                                                                               |
| Verification    | 2024-02-04_22-24-14_result_file.csv                                                 | 2024-02-04_22-28-31_result_file.csv                                                 | 2024-02-04_22-29-21_result_file.csv                                                 |
| Speedups        | 0                                                                                   | 0                                                                                   | 0                                                                                   |
| Average Speedup | 1.88                                                                                | 2.26                                                                                | 2.11                                                                                |
| Median Speedup  | 1.88                                                                                | 2.26                                                                                | 2.11                                                                                |
| Fastest Speedup | 1.88                                                                                | 2.26                                                                                | 2.11                                                                                |

#### other networks - for comparison - prop_0_0.03.vnnlib
##### from 1
| Metric          | Student1                                                                             | Student2                                                                           | Student3 |
|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|----------|
| File            | 2024_02_04_11_49_42_options.json_Options__0.9667999744415283_f1Score__18_Epoch.onnx	 | 2024_02_04_12_03_16_options.json_Options__0.9703999757766724_f1Score__8_Epoch.onnx |          |
| F1-Score        |                                                                                      |                                                                                    |          |
| Verification    | 2024-02-04_13-09-50_result_file.csv	                                                 | 2024-02-04_19-46-24_result_file.csv                                                |          |
| Speedups        | 0                                                                                    | 0                                                                                  |          |
| Average Speedup | 83.0                                                                                 | 13.75                                                                              |          |
| Median Speedup  | 83.0                                                                                 |                                                                                    |          |
| Fastest Speedup | 83.0                                                                                 |                                                                                    |          |

##### from 2
| Metric          | Student1                                                                            | Student2                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_12_38_28_options.json_Options__0.9664999842643738_f1Score__17_Epoch.onnx | 2024_02_04_12_47_21_options.json_Options__0.9722999930381775_f1Score__12_Epoch.onnx |
| F1-Score        | 0.966                                                                               | 0.972                                                                               |
| Verification    | 2024-02-04_21-14-30_result_file.csv                                                 | 2024-02-04_22-34-00_result_file.csv                                                 |
| Speedups        | 0                                                                                   | 0                                                                                   |
| Average Speedup | 143.18                                                                              | 252.30                                                                              |
| Median Speedup  |                                                                                     |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                     |

##### from 4
| Metric          | Student1                                                                            | Student2                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_14_13_43_options.json_Options__0.9835000038146973_f1Score__16_Epoch.onnx | 2024_02_04_14_26_19_options.json_Options__0.9825999736785889_f1Score__14_Epoch.onnx |
| F1-Score        | 0.9835                                                                              | 0.9826                                                                              |
| Verification    | 2024-02-05_08-14-06_result_file.csv                                                 | 2024-02-05_09-20-41_result_file.csv                                                 |
| Speedups        |                                                                                     |                                                                                     |
| Average Speedup | 874.92                                                                              | 1141.01                                                                             |
| Median Speedup  |                                                                                     |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                     |

##### from 5
| Metric          | Student1                                                                          | Student2                                                                          |
|-----------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| File            | 2024_02_04_14_41_43_options.json_Options__0.855400025844574_f1Score__8_Epoch.onnx | 2024_02_04_14_46_43_options.json_Options__0.858299970626831_f1Score__4_Epoch.onnx |
| F1-Score        | 0.8554                                                                            | 0.8583                                                                            |
| Verification    | 2024-02-04_18-10-00_result_file.csv                                               | 2024-02-04_17-20-15_result_file.csv                                               |
| Speedups        |                                                                                   |                                                                                   |
| Average Speedup | 1.67                                                                              | 52.70                                                                             |
| Median Speedup  |                                                                                   |                                                                                   | 
| Fastest Speedup |                                                                                   |                                                                                   | 






#### Especially trained for this category - prop_3_0.03.vnnlib
Differences to 3:
 - vnnlibs_path: from "" to "vnncomp2022_benchmarks/benchmarks/mnist_fc/vnnlib/prop_3_0.03.vnnlib"
 - dataset: from MNIST to RANDOM_INPUTS

Notice: Prediction (hard labels) are always the same, since this network has only been **trained for one property**. F1-Score on whole dataset therefore is bad - everything is classified as the same, which is correct in about 1/10 of the cases. 

**Verification-Speedup is only validated on the property, the network has been trained for!**

Therefor, the speedups here are not comparable to other speedups, because of high variance in the speedups verification-instance. 

| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_13_09_56_51_options.json_Options__0.09849999845027924_f1Score__0_Epoch.onnx | 2024_02_13_09_59_02_options.json_Options__0.09849999845027924_f1Score__0_Epoch.onnx | 2024_02_13_10_01_10_options.json_Options__0.09849999845027924_f1Score__0_Epoch.onnx |
| F1-Score        |                                                                                     |                                                                                     |                                                                                     |
| Verification    | 2024-02-18_10-39-41_result_file.csv                                                 | 2024-02-18_10-41-19_result_file.csv                                                 | 2024-02-18_10-42-15_result_file.csv                                                 |
| Speedups        |                                                                                     |                                                                                     |                                                                                     |
| Average Speedup | 1.82                                                                                | 1.93                                                                                | 2.18                                                                                |
| Median Speedup  |                                                                                     |                                                                                     |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                     |                                                                                     |

#### other networks - for comparison - prop_3_0.03.vnnlib
##### from 1
| Metric          | Student1                                                                             | Student2                                                                           | Student3 |
|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|----------|
| File            | 2024_02_04_11_49_42_options.json_Options__0.9667999744415283_f1Score__18_Epoch.onnx	 | 2024_02_04_12_03_16_options.json_Options__0.9703999757766724_f1Score__8_Epoch.onnx |          |
| F1-Score        |                                                                                      |                                                                                    |          |
| Verification    | 2024-02-04_13-09-50_result_file.csv	                                                 | 2024-02-04_19-46-24_result_file.csv                                                |          |
| Speedups        | 0                                                                                    | 0                                                                                  |          |
| Average Speedup | 67.12                                                                                | 2.34                                                                               |          |

##### from 2
| Metric          | Student1                                                                            | Student2                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_12_38_28_options.json_Options__0.9664999842643738_f1Score__17_Epoch.onnx | 2024_02_04_12_47_21_options.json_Options__0.9722999930381775_f1Score__12_Epoch.onnx |
| F1-Score        | 0.966                                                                               | 0.972                                                                               |
| Verification    | 2024-02-04_21-14-30_result_file.csv                                                 | 2024-02-04_22-34-00_result_file.csv                                                 |
| Speedups        | 0                                                                                   | 0                                                                                   |
| Average Speedup | 24.23                                                                               | 2.16                                                                                |
| Median Speedup  |                                                                                     |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                     |

##### from 4
| Metric          | Student1                                                                            | Student2                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_04_14_13_43_options.json_Options__0.9835000038146973_f1Score__16_Epoch.onnx | 2024_02_04_14_26_19_options.json_Options__0.9825999736785889_f1Score__14_Epoch.onnx |
| F1-Score        | 0.9835                                                                              | 0.9826                                                                              |
| Verification    | 2024-02-05_08-14-06_result_file.csv                                                 | 2024-02-05_09-20-41_result_file.csv                                                 |
| Speedups        |                                                                                     |                                                                                     |
| Average Speedup | 2.21                                                                                | 2.12                                                                                |
| Median Speedup  |                                                                                     |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                     |

##### from 5
| Metric          | Student1                                                                          | Student2                                                                          |
|-----------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| File            | 2024_02_04_14_41_43_options.json_Options__0.855400025844574_f1Score__8_Epoch.onnx | 2024_02_04_14_46_43_options.json_Options__0.858299970626831_f1Score__4_Epoch.onnx |
| F1-Score        | 0.8554                                                                            | 0.8583                                                                            |
| Verification    | 2024-02-04_18-10-00_result_file.csv                                               | 2024-02-04_17-20-15_result_file.csv                                               |
| Speedups        |                                                                                   |                                                                                   |
| Average Speedup | 2.27                                                                              | 2.29                                                                              |
| Median Speedup  |                                                                                   |                                                                                   | 
| Fastest Speedup |                                                                                   |                                                                                   | 

### 7

Differences to 4: 
   - student_model: from "minst_fc_784_256_10" to "mnist_fc_784_256_256_256_10",


| Metric          | Student1                                                                            | Student2                                                                           | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_18_10_59_18_options.json_Options__0.9840999841690063_f1Score__18_Epoch.onnx | 2024_02_18_11_04_26_options.json_Options__0.983299970626831_f1Score__15_Epoch.onnx | 2024_02_18_11_09_39_options.json_Options__0.9837999939918518_f1Score__16_Epoch.onnx |
| F1-Score        |                                                                                     |                                                                                    |                                                                                     |
| Verification    | 2024-02-18_11-22-54_result_file.csv                                                 |                                                                                    | 2024-02-18_12-22-01_result_file.csv                                                 |
| Speedups        | 0                                                                                   |                                                                                    | 0                                                                                   |
| Average Speedup | 234.14                                                                              |                                                                                    | 235.67                                                                              |
| Median Speedup  | 37.677                                                                              |                                                                                    | 36.29                                                                               |
| Fastest Speedup | 1.28                                                                                |                                                                                    | 1.31                                                                                |

### 8

Differences to 4:
 - criterion: from "CrossEntropyLoss" to "MSELoss"


| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                           |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| File            | 2024_02_26_10_39_58_options.json_Options__0.9761000275611877_f1Score__13_Epoch.onnx | 2024_02_26_10_44_39_options.json_Options__0.9733999967575073_f1Score__14_Epoch.onnx | 2024_02_26_10_49_57_options.json_Options__0.9718000292778015_f1Score__6_Epoch.onnx |
| F1-Score        | 0.976                                                                               | 0.973                                                                               | 0.971                                                                              |
| Verification    | 2024-02-26_11-49-07_result_file.csv                                                 |                                                                                     | 2024-02-26_12-36-59_result_file.csv                                                |
| Speedups        | 0                                                                                   |                                                                                     | 2                                                                                  |
| Average Speedup | 88.98                                                                               |                                                                                     | 18.33                                                                              |
| Median Speedup  | 17.55                                                                               |                                                                                     | 4.58                                                                               |
| Fastest Speedup | 1.05                                                                                |                                                                                     | 0.11                                                                               | 

## mnist-net_256x4.onnx

### 1 
Differences to 256x2 - 4:
 - student_model: from "minst_fc_784_256_10" to "mnist_fc_784_256_256_10"
  - teacher_path: from ".../mnist-net_256x2.onnx" to ".../mnist-net_256x4.onnx"


| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                           |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| File            | 2024_02_05_10_37_29_options.json_Options__0.9825000166893005_f1Score__17_Epoch.onnx | 2024_02_05_10_42_47_options.json_Options__0.9828000068664551_f1Score__11_Epoch.onnx | 2024_02_05_10_47_51_options.json_Options__0.9825999736785889_f1Score__7_Epoch.onnx |
| F1-Score        | 0.9825                                                                              | 0.9828                                                                              | 0.9826                                                                             |
| Verification    |                                                                                     | 2024-02-05_10-59-56_result_file.csv                                                 | 2024-02-05_14-38-37_result_file.csv                                                |
| Speedups        |                                                                                     | 1                                                                                   | 0                                                                                  |
| Average Speedup |                                                                                     | 27.60                                                                               | 4.38                                                                               |
| Median Speedup  |                                                                                     | 1.88                                                                                | 2.1                                                                                |
| Fastest Speedup |                                                                                     | 0.97                                                                                | 1.04                                                                               |

Here way more often timeout is reached - even for collecting splits on the small network already. This causes the verification time to be the about the same. 

### 2
Differences to 256x2 - 5: 
 - student_model: from "minst_fc_784_256_10" to "mnist_fc_784_256_256_10"
  - teacher_path: from ".../mnist-net_256x2.onnx" to ".../mnist-net_256x4.onnx"


| Metric          | Student1                                                                            | Student2                                                                          | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_05_17_48_32_options.json_Options__0.8500999808311462_f1Score__11_Epoch.onnx | 2024_02_05_17_52_54_options.json_Options__0.847599983215332_f1Score__6_Epoch.onnx | 2024_02_05_17_57_24_options.json_Options__0.8366000056266785_f1Score__18_Epoch.onnx |
| F1-Score        |                                                                                     |                                                                                   |                                                                                     |
| Verification    |                                                                                     |                                                                                   |                                                                                     |
| Speedups        |                                                                                     |                                                                                   |                                                                                     |
| Average Speedup |                                                                                     |                                                                                   |                                                                                     |
| Median Speedup  |                                                                                     |                                                                                   |                                                                                     |
| Fastest Speedup |                                                                                     |                                                                                   |                                                                                     |

### 3
Small networks used for verification in this chapter (verification of 256x4) were trained not on 256x4 but 256x2. 


| Metric          | Student1                                                                            | Student2                                                                          | Student3 |
|-----------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|----------|
| File            | 2024_02_04_14_13_43_options.json_Options__0.9835000038146973_f1Score__16_Epoch.onnx | 2024_02_04_14_46_43_options.json_Options__0.858299970626831_f1Score__4_Epoch.onnx |          |
| F1-Score        | 0.984                                                                               | 0.858                                                                             |          |
| Verification    | 2024-02-12_15-18-36_result_file.csv                                                 | 2024-02-12_11-54-36_result_file.csv                                               |          |
| Speedups        | 0                                                                                   | 1                                                                                 |          |
| Average Speedup | 518.96                                                                              | 10.22                                                                             |          |
| Median Speedup  | 82.98                                                                               | 1.81                                                                              |          |
| Fastest Speedup | 2.0                                                                                 | 0.76                                                                              |          |

## own teacher: 2024_02_20_10_46_42_options.json_Options__0.9854999780654907_f1Score__19_Epoch.onnx

### 1
Differences to mnist-net_256x2.onnx - 4
   - teacher_path: from "mnist-net_256x2.onnx" to "2024_02_20_10_46_42_options.json_Options__0.9854999780654907_f1Score__19_Epoch.onnx"
   - criterion: from "CrossEntropyLoss" to "MSELoss"
      - did not work with CrossEntropyLoss -> everything was classified as the same class
      
| Metric          | Student1                                                                           | Student2                                                                            | Student3                                                                            |
|-----------------|------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_20_11_36_49_options.json_Options__0.986299991607666_f1Score__19_Epoch.onnx | 2024_02_20_11_42_41_options.json_Options__0.9847000241279602_f1Score__18_Epoch.onnx | 2024_02_20_11_47_46_options.json_Options__0.9854000210762024_f1Score__16_Epoch.onnx |
| F1-Score        |                                                                                    |                                                                                     |                                                                                     |
| Verification    | 2024-02-20_12-07-37_result_file.csv                                                | 2024-02-20_15-13-11_result_file.csv                                                 |                                                                                     |
| Speedups        | 0                                                                                  | 1                                                                                   |                                                                                     |
| Average Speedup | 4.06                                                                               | 3.68                                                                                |                                                                                     |
| Median Speedup  | 1.94                                                                               | 2.16                                                                                |                                                                                     |
| Fastest Speedup | 1.07                                                                               | 0.008                                                                               |                                                                                     |

### 2
Differences to 1:
   - student_model: from "minst_fc_784_256_10" to "mnist_fc_784_64_10"

| Metric          | Student1                                                                            | Student2                                                                           | Student3                                                                           |
|-----------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| File            | 2024_02_21_10_52_19_options.json_Options__0.9686999917030334_f1Score__11_Epoch.onnx | 2024_02_21_10_56_05_options.json_Options__0.963699996471405_f1Score__19_Epoch.onnx | 2024_02_21_11_00_00_options.json_Options__0.970300018787384_f1Score__16_Epoch.onnx |
| F1-Score        |                                                                                     |                                                                                    |                                                                                    |
| Verification    |                                                                                     |                                                                                    | 2024-02-21_11-22-18_result_file.csv                                                |
| Speedups        |                                                                                     |                                                                                    | 1                                                                                  |
| Average Speedup |                                                                                     |                                                                                    | 2.65                                                                               |
| Median Speedup  |                                                                                     |                                                                                    | 2.04                                                                               |
| Fastest Speedup |                                                                                     |                                                                                    | 0.92                                                                               |

### 3
Differences to 1:
   - student_model: from "minst_fc_784_256_10" to "mnist_fc_784_32_10"

| Metric          | Student1                                                                            | Student2                                                                            | Student3                                                                            |
|-----------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| File            | 2024_02_21_12_47_20_options.json_Options__0.9466999769210815_f1Score__16_Epoch.onnx | 2024_02_21_12_54_47_options.json_Options__0.9391000270843506_f1Score__19_Epoch.onnx | 2024_02_21_13_00_46_options.json_Options__0.9372000098228455_f1Score__14_Epoch.onnx |
| F1-Score        |                                                                                     |                                                                                     |                                                                                     |
| Verification    | 2024-02-21_13-08-00_result_file.csv                                                 |                                                                                     | 2024-02-21_14-30-50_result_file.csv                                                 |
| Speedups        | 0                                                                                   |                                                                                     | 0                                                                                   |
| Average Speedup | 2.48                                                                                |                                                                                     | 1.79                                                                                |
| Median Speedup  | 2.07                                                                                |                                                                                     | 1.87                                                                                |
| Fastest Speedup | 1.05                                                                                |                                                                                     | 1.01                                                                                |

# Raw table (unfilled)

| Metric          | Student1 | Student2 | Student3 |
|-----------------|----------|----------|----------|
| File            |          |          |          |
| F1-Score        |          |          |          |
| Verification    |          |          |          |
| Speedups        |          |          |          |
| Average Speedup |          |          |          |
| Median Speedup  |          |          |          |
| Fastest Speedup |          |          |          | 


