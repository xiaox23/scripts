import sys
import os
import argparse
from dexhand_client import DexHandClient
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Tac-3D/DexHand-SDK-v1.1/pyDexHandClient/examples')))
import PyTac3D
import time
import pickle
from datetime import datetime

def get_timestamp():
    return str(int(time.time() * 1000 - 100))  # 100ms延迟

# 将数据保存到指定子文件夹中，子文件夹路径由实验编号生成
def save_to_pickle(data, base_folder, exp_number):
    """
    保存数据到指定的子文件夹中。
    Args:
        data (dict): 要保存的数据。
        base_folder (str): 存放所有实验数据的主文件夹路径。
        exp_number (str): 当前实验编号，用于创建子文件夹。
    """
    try:
        # 构造子文件夹路径
        sub_folder = os.path.join(base_folder, exp_number.zfill(4))
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        
        # 自动生成文件名
        file_name = f"{get_timestamp()}.pkl"
        file_path = os.path.join(sub_folder, file_name)

        # 保存数据到 pickle 文件
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

        # 返回子文件夹路径
        return sub_folder

    except Exception as e:
        print(f"Error saving data to {sub_folder}: {e}")

# 用于存储 Tac3D 的测量结果
class Tac3D_info:
    def __init__(self, SN):
        self.SN = SN  # 传感器 SN
        self.P = np.zeros((400, 3))  # 三维形貌测量结果
        self.D = np.zeros((400, 3))  # 三维变形场测量结果
        self.F = np.zeros((400, 3))  # 三维分布力场测量结果
        self.Fr = np.zeros((1, 3))  # 三维合力
        self.Mr = np.zeros((1, 3))  # 三维合力矩

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="DexHand data collection with Tac3D.")
    parser.add_argument(
        '--folder_path',
        type=str,
        default='data_save/tac_data',
        help="Path to the folder where the data will be saved (default: 'data_save/tac_data')"
    )
    parser.add_argument(
        '--exp_number',
        type=str,
        required=True,
        help="Experiment number (e.g., '0001', '0002')."
    )
    args = parser.parse_args()
    folder_path = args.folder_path
    exp_number = args.exp_number

    # Tac3D 的回调函数
    def Tac3DRecvCallback(frame, param):
        # 获取 SN
        SN = frame["SN"]  # 通过 SN 号确定哪一个 Tac3D 调用了回调函数
        tacinfo = param[SN]

        # 获取标志点三维形貌
        P = frame.get("3D_Positions")
        tacinfo.P = P

        # 获取标志点三维位移场
        D = frame.get("3D_Displacements")
        tacinfo.D = D

        # 获取三维分布力
        F = frame.get("3D_Forces")
        tacinfo.F = F

        # 获得三维合力
        Fr = frame.get("3D_ResultantForce")
        tacinfo.Fr = Fr

        # 获得三维合力矩
        Mr = frame.get("3D_ResultantMoment")
        tacinfo.Mr = Mr

    # 机械手的回调函数
    def HandRecvCallback(client: DexHandClient):
        info = client.hand_info
        # DexHand 本体信息的回传频率为 100Hz
        if info._frame_cnt % 2 == 0:
            # 创建保存的字典数据
            data = {
                "pos": info.now_pos,
                "force": info.avg_force,
                "P1": tacinfo1.P,
                "D1": tacinfo1.D,
                "F1": tacinfo1.F,
                "Fr1": tacinfo1.Fr,
                "Mr1": tacinfo1.Mr,
                "P2": tacinfo2.P,
                "D2": tacinfo2.D,
                "F2": tacinfo2.F,
                "Fr2": tacinfo2.Fr,
                "Mr2": tacinfo2.Mr
            }

            # 调用保存函数，传入主文件夹路径和实验编号
            sub_folder = save_to_pickle(data, folder_path, exp_number)
            
            # 返回子文件夹路径
            return sub_folder

    # 创建机械手客户端
    client = DexHandClient(ip="192.168.2.100", port=60031, recvCallback_hand=HandRecvCallback)
    # 创建传感器数据存储实例
    Tac3D_name1 = "HDL1-GWH0017"
    Tac3D_name2 = "HDL1-GWH0018"
    tacinfo1 = Tac3D_info(Tac3D_name1)
    tacinfo2 = Tac3D_info(Tac3D_name2)
    tac_dict = {Tac3D_name1: tacinfo1, Tac3D_name2: tacinfo2}
    # 创建传感器实例
    tac3d = PyTac3D.Sensor(recvCallback=Tac3DRecvCallback, port=9988, maxQSize=5, callbackParam=tac_dict)
    # 启动机械手
    client.start_server()
    client.acquire_hand()
    client.set_home()
    client.calibrate_force_zero()
    tac3d.calibrate(Tac3D_name1)
    tac3d.calibrate(Tac3D_name2)

    print("Press 'z' to execute contact and grasp commands...")
    while True:
        key = input("Input key: ").strip().lower()
        if key == "z":
            client.contact(contact_speed=8, preload_force=2, quick_move_speed=15, quick_move_pos=10)
            client.grasp(goal_force=8.0, load_time=8.0)
            print("Contact and grasp commands executed.")
            time.sleep(3)
            current_time = int(1000 * round(time.time(), 3))
            
            # 保存时间戳到与 pkl 文件相同的文件夹
            sub_folder = os.path.join(folder_path, exp_number.zfill(4))
            time_file_path = os.path.join(sub_folder, "grasp_time.txt")
            try:
                with open(time_file_path, "a") as file:
                    file.write(f"{current_time}\n")
            except Exception as e:
                print(f"Failed to save timestamp: {e}")
                break
            print(f"Time saved to {time_file_path}")
            break

    print("Press 'f' to release the hand...")
    while True:
        key = input("Input key: ").strip().lower()
        if key == "f":
            client.release_hand()
            print("Hand control released.")
            break
# python scripts/F01TacData.py --folder_path data_save/tac_data --exp_number 1