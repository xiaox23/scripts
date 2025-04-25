# version instruction
## C0 version
版本功能：

``` sh scripts/run_Cscripts.sh ```

同时运行视觉和触觉的采集代码。

``` python scripts/C03pair_data.py ```

以视觉代码为基准，对齐最近帧的触觉数据，并且保存成新的pickle文件。

``` python scripts/C04vis_data.py ```

可视化视觉数据和触觉传感器的形貌数据。

## D0 version
版本功能：

``` python scripts/C01TacData.py --folder_path data_save/tac_data ```

运行触觉的采集代码，会记录下夹爪的根部力信号和位置信号。也会记录下夹爪之间的marker形貌、位移变化、受力和平均三维力和平均三维力矩。

``` python scripts/D07duiqi.py ```

对齐根部（无延迟信号）和触觉marker信号。
