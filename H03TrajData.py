#!/usr/bin/env python3

"""
Description: record data (action and timestamp) using teleoperation with spacemouse and save as pkl
"""

import numpy as np
import argparse
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../xArm-Python-SDK/control')))
from spacemouse import Spacemouse
import pickle as pkl
import threading
import select

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def create_formated_skill_dict(joints, end_effector_positions, timestamps):
    """
    创建标准化技能字典
    参数:
        joints: 关节角度列表, 每个元素是6个关节角度的数组
        end_effector_positions: 末端位姿列表, 每个元素是[x,y,z,roll,pitch,yaw]
        timestamps: 时间戳列表
    返回:
        格式化后的字典,适合保存为pkl
    """
    skill_dict = {
        'skill_description': 'GuideMode',
        'skill_state_dict': {
            'q': joints,
            'O_T_EE': end_effector_positions,
            'time_since_skill_started': timestamps
        }
    }
    return {0: skill_dict}

class DataRecorder:
    def __init__(self, args):
        self.args = args
        self.running = True
        self.arm = XArmAPI(args.ip, is_radian=True)
        self.record_data = {
            'joints': [],
            'end_effector_positions': [],
            'timestamps': []
        }

    def stop_on_keypress(self):
        """监听标准输入，当用户输入 'o' 时停止运行"""
        print("Press 'o' to stop...")
        while self.running:
            if select.select([sys.stdin], [], [], 0)[0]:
                user_input = sys.stdin.readline().strip()
                if user_input.lower() == 'o':
                    print("Stopping...")
                    self.running = False
                    break

    def record_data_loop(self):
        self.arm.motion_enable(enable=True)
        self.arm.set_mode(0)
        self.arm.set_state(state=0)
        # self.arm.move_gohome(wait=True)
        angle = [91.023055, -41.685945, -36.419547, 4.527684, 72.765411, -45.556103, 0.0]
        self.arm.set_servo_angle(angle=angle, speed=50, is_radian=False, wait=True)

        print('Ready...')
        self.arm.set_mode(7)
        self.arm.set_state(0)
        time.sleep(1)

        max_pos_speed = 0.15
        max_rot_speed = 0.25
        dt = 2
        speed = 60

        target_pose = self.arm.get_position(is_radian=False)
        # start_time = time.time()
        # last_time = None
        position = target_pose[1][:3]
        rotation = target_pose[1][3:]

        with Spacemouse(deadzone=0.3) as sm:
            while self.running:
                # Record data
                self.record_data['joints'].append(self.arm.get_servo_angle(is_radian=False)[1])
                self.record_data['end_effector_positions'].append(self.arm.get_position(is_radian=False)[1])
                self.record_data['timestamps'].append(str(int(time.time() * 1000)))

                # Spacemouse motion handling
                sm_state = sm.get_motion_state_transformed()
                dpos = sm_state[:3] * (max_pos_speed * dt)
                drot = sm_state[3:] * (max_rot_speed * dt)

                if not sm.is_button_pressed(0):
                    drot[:] = 0
                else:
                    dpos[:] = 0

                position += dpos
                rotation += drot

                self.arm.set_position(x=position[0], y=position[1], z=position[2],
                                      roll=rotation[0], pitch=rotation[1], yaw=rotation[2],
                                      speed=speed, wait=False, is_radian=False)

                time.sleep(0.01)
                # last_time = time.time()

        # Save data after stopping
        skill_dict = create_formated_skill_dict(
            self.record_data['joints'],
            self.record_data['end_effector_positions'],
            self.record_data['timestamps']
        )

        try:
            sub_folder = os.path.join(self.args.path, self.args.exp_number.zfill(4))
            if not os.path.exists(sub_folder):
                os.makedirs(sub_folder)

            file_name = f"{self.args.exp_number.zfill(4)}.pkl"
            file_path = os.path.join(sub_folder, file_name)

            with open(file_path, 'wb') as f:
                pkl.dump(skill_dict, f)
        except Exception as e:
            print(f"Error saving data to {sub_folder}: {e}")

        # 安全关闭
        self.arm.set_mode(0)
        self.arm.disconnect()

    def run(self):
        # Start keypress listener in a separate thread
        keypress_thread = threading.Thread(target=self.stop_on_keypress)
        keypress_thread.start()

        # Start the data recording loop
        self.record_data_loop()

        # Wait for the keypress thread to finish
        keypress_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_number', type=str, required=True, help="Experiment number (e.g., '0001', '0002').")
    parser.add_argument('--path', '-p', default='data_save/traj_data')
    parser.add_argument('--ip', default='192.168.1.228', help='xArm IP address')
    args = parser.parse_args()

    recorder = DataRecorder(args)
    recorder.run()


# python scripts/G03TrajData.py --exp_number 4
