# 第三关：构建与运行说明

## 环境

本地验证环境：WSL2、Ubuntu 24.04.5 LTS、
G++ 13.3.0、Python 3.12.3。
需要支持 C++17 和 OpenMP 的 G++。
Python 不需要第三方依赖，详见 requirements.txt。

以下命令均在本文件所在目录执行。

## 文件说明

- baseline_old.cpp：保留的原始串行代码。
- baseline_serial.cpp：抽取 filter_records 接口后的串行版。
- filter_openmp.cpp：抽取接口并修正计时范围后的并行版。
- support.hpp：公共数据结构、数据生成、文件读写和参考校验。
- test_public.py：保留的公开测试。
- test_regression.py：新增回归测试。
- evidence/：测试记录、环境信息和原始性能测量。

其余 baseline*.cpp 文件为早期开发备份，本说明不使用它们构建。

## 编译

```bash
g++ -std=c++17 baseline_serial.cpp -O2 -o log_filter_serial
g++ -std=c++17 filter_openmp.cpp -O2 -fopenmp -o log_filter_openmp
```

## 正确性测试

```bash
python3 test_public.py ./log_filter_serial
python3 test_public.py ./log_filter_openmp
python3 test_regression.py
```

公开测试通过时显示 OK。
新增测试通过时显示 OK: 40 program checks passed。

## 性能测量

下面每个程序内部先预热 1 次，再记录 5 次正式样本。

```bash
./log_filter_serial --count 1000000 --seed 2026 --hit-percent 50 --pattern random --repeats 5
OMP_NUM_THREADS=20 OMP_DYNAMIC=FALSE ./log_filter_openmp --count 1000000 --seed 2026 --hit-percent 50 --pattern random --repeats 5
```

第二组将两条命令中的 --count 改为 10000000，其余参数保持一致。
默认查询为时间区间 [1000,2000)、延迟至少 100、标记包含 3 的全部位。

core_ms 为筛选函数调用耗时，包含输出写入。
并行版还包含临时容器创建、扩容、释放、并行区域执行及结果合并。
输入生成、输入输出文件读写、参考校验和控制台打印不在核心计时内。
输入和最终输出缓冲区由调用方在计时前准备。

median_core_ms 为 5 次正式样本的中位数。
加速比 = 串行版中位数 / 并行版中位数。
threads_max 表示 OpenMP 最大线程数设置，并非在并行区域内直接测得的团队大小。

## 提交状态

本说明用于本地复现。
正式平台的入口和打包细节仍需核对官方 README；
本地测试通过不等于正式 checker 已通过。
