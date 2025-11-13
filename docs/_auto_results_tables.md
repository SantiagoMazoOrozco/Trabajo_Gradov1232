### 4.1 Descriptivos (batch 20251027, medianas y medias)
| Stage | Group | time_ms (med/mean) | cpu_avg% (med/mean) | mem_peak_mb (med/mean) | records_per_s (med/mean) | watts_per_mb (med/mean) |
|---|---|---:|---:|---:|---:|---:|
| TRAIN_RF | control | 1781.030/1785.152 | 30.345/32.238 | 190.769/191.081 | 1348.189/1346.414 | 47.675/52.559 |
| TRAIN_RF | treatment | 1773.894/1769.241 | 30.640/32.163 | 193.727/193.864 | 1353.601/1357.479 | 50.305/51.785 |
| TRAIN_SVM | control | 203.090/203.252 | 27.000/31.025 | 190.769/191.231 | 11817.402/11808.020 | 4.992/5.738 |
| TRAIN_SVM | treatment | 203.642/203.600 | 27.125/29.025 | 193.790/193.877 | 11785.376/11787.840 | 5.029/5.375 |

### 5.1.1 Resumen de p-values (permutación)
| Stage | Métrica | p-value | Interpretación |
|---|---|---:|---|
| TRAIN_RF | time_ms | 0.3627 | No significativo |
| TRAIN_SVM | time_ms | 0.9098 | No significativo |
| TRAIN_RF | records_per_s | 0.4727 | No significativo |
| TRAIN_SVM | records_per_s | 0.9462 | No significativo |
