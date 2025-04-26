# Read me

## 仓库下载

### 创建文件夹
```
mkdir -p real
cd real
```

### 下载scripts仓库
```
git clone https://github.com/xiaox23/scripts.git
```

## 下载Tac3D仓库


记得先激活夹爪
```
python Tac-3D/DexHand-SDK-v1.1/pyDexHandClient/examples/activate_service.py
```

检查端口占用
```
sudo lsof -i :9988
```
清除报错
```
python Tac-3D/DexHand-SDK-v1.1/pyDexHandClient/control/safe.py
```

## F0 version
版本功能：

```
sh scripts/run_Fscripts.sh
```

运行触觉+视觉的采集代码，但是记得修改实验次数！！！每次数据采集都要修改

```
python scripts/F03pair_data.py
```

对于原始信号做一个对齐处理，把视觉数据和触觉数据一起保存在新的文件夹```data_save/combined_data```中。认为夹爪抓紧时候为起点，删掉之前的数据。

```
python scripts/F04cal_data.py
```

调整数据格式，然后处理数据，使得能够绘制markerflow的图像。新数据保存在```data_save/cal_data```。

```
python scripts/F05vis_data.py
```

绘图，保存在```data_save/cal_plots```。


## C0 version
版本功能：

```
sh scripts/run_Cscripts.sh
```

同时运行视觉和触觉的采集代码。

```
python scripts/C03pair_data.py
```

以视觉代码为基准，对齐最近帧的触觉数据，并且保存成新的pickle文件。

```
python scripts/C04vis_data.py
```

可视化视觉数据和触觉传感器的形貌数据。

## D0 version
版本功能：

```
python scripts/C01TacData.py --folder_path data_save/tac_data
```

运行触觉的采集代码，会记录下夹爪的根部力信号和位置信号。也会记录下夹爪之间的marker形貌、位移变化、受力和平均三维力和平均三维力矩。

```
python scripts/D07duiqi.py
```

对齐根部（无延迟信号）和触觉marker信号。
