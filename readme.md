# Read me

## 仓库下载

### 1. 创建文件夹
```
mkdir -p real
cd real
```

### 2. 下载scripts仓库
```
git clone https://github.com/xiaox23/scripts.git
```

### 3. 下载Tac3D仓库

```
git clone https://github.com/xiaox23/Tac-3D.git
```

### 4. 下载Realsense仓库

```
git clone https://github.com/xiaox23/collect_RGBD.git
```

## 环境和真机setup
### 1. 触觉
```
cd Tac-3D
```
创建&激活环境
```
conda create -n real python=3.8
conda activate real
```

安装Tac3D需要的包
```
cd DexHand-SDK-v1.1/pyDexHandClient
pip install .
```

Tac3D和电脑通过网线连接，需要将有线网的ip设置如下：

![alt text](readme_pic/image.png)

运行激活demo
```
cd ../../../
python DexHand-SDK-v1.1/pyDexHandClient/examples/activate_service.py
```
终端输出下面的表示正常激活
```
[UDP Manager] Client at: 0.0.0.0 : 42044
[UDP Manager] Receiver at: 224.0.2.100 : 60031
[INFO] Client: Start DexHand client.
[INFO] Client: Try to start DexHand server.
[INFO] Server: Starting server...
[INFO] Hand: DexHand has initialized successfully.
[INFO] Tac3D: Tac3D has initialized successfully
[INFO] Server: Started.
[INFO] Client: exiting program.
```

运行其他夹爪demo
```
python DexHand-SDK-v1.1/pyDexHandClient/examples/get_info.py
```

```
python DexHand-SDK-v1.1/pyDexHandClient/examples/grasp_force_control.py
```

```
python DexHand-SDK-v1.1/pyDexHandClient/examples/move_dexhand.py
```
运行触觉demo需要先安装一些包
```
pip install numpy ruamel.yaml vedo==2023.4.6 vtk==9.1.0  # 视触觉传感器要用的库
pip install opencv-python
```
检查包有没有安装成功
```
pip list | grep vedo
pip list | grep vtk
```
输出如下，安装成功
```
vedo                          2023.4.6
vtk                           9.1.0
```
运行触觉demo

```
python DexHand-SDK-v1.1/pyDexHandClient/examples/PyTac3D.py
```

```
# 下面的内容要在运行前修改
# Tac3D_name1 = "HDL1-GWH0017"
# Tac3D_name2 = "HDL1-GWH0018"
python DexHand-SDK-v1.1/pyDexHandClient/examples/handandtac3d.py
```

### 2. 视觉
```
cd ..
git clone https://github.com/IntelRealSense/librealsense
```

```
cd librealsense
sudo apt-get install libudev-dev pkg-config libgtk-3-dev
sudo apt-get install libusb-1.0-0-dev pkg-config
sudo apt-get install libglfw3-dev
sudo apt-get install libssl-dev
```

```
mkdir build
cd build
cmake ../ -DBUILD_EXAMPLES=true
make
sudo make install 
```
运行视觉gui
```
realsense-viewer
```
安装视觉python包
```
pip install pyrealsense2
```
运行视觉demo
```
cd ../../
cd collect_RGBD
python pyrealsense2/realsense.py
cd ..
```

## 实机数据采集脚本使用说明

记得先激活夹爪
```
python Tac-3D/DexHand-SDK-v1.1/pyDexHandClient/examples/activate_service.py
```

### 1. F0 version
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

### 2. 常见问题
检查端口占用
```
sudo lsof -i :9988
```
清除报错
```
python Tac-3D/DexHand-SDK-v1.1/pyDexHandClient/control/safe.py
```
### C0 version
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

### D0 version
版本功能：

```
python scripts/C01TacData.py --folder_path data_save/tac_data
```

运行触觉的采集代码，会记录下夹爪的根部力信号和位置信号。也会记录下夹爪之间的marker形貌、位移变化、受力和平均三维力和平均三维力矩。

```
python scripts/D07duiqi.py
```

对齐根部（无延迟信号）和触觉marker信号。
