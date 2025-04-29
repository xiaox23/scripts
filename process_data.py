import os
import torch
import numpy as np
import cv2
import open3d as o3d
import random
import pickle
from tqdm import tqdm
import math
from pointnet2_ops import pointnet2_utils

    
def get_pt_files(directory):
    pt_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pt'):
                pt_files.append(os.path.join(root, file))
    return pt_files
    
def get_pcd_from_rgbd(depth, rgb, mask):
    fx = 595.8051147460938
    fy = 595.8051147460938
    cx = 315.040283203125
    cy = 246.26866149902344
    height, width = depth.shape 
    u, v = np.meshgrid(np.arange(width), np.arange(height))
    Z = depth
    X = (u - cx) * Z / fx
    Y = (v - cy) * Z / fy
    point_cloud = np.dstack((X, Y, Z))
    point_cloud = point_cloud[mask]
    rgb = rgb[mask]
    pcd = np.concatenate((point_cloud.reshape(-1, 3), rgb.reshape(-1, 3)), axis=-1)

    return pcd.astype(np.float32)

def transform_pcd(pcd, c2w):
    pcd[:, :3] = np.dot(pcd[:, :3], c2w[:3, :3].T) + c2w[:3, 3]

    return pcd

def process_pcd(pcd):
    xyz = pcd[:, :3]
    xyz /= 0.2
    xyz_mean = np.mean(xyz, axis=0)
    pcd[:, :3] = xyz
    distances = np.linalg.norm(xyz - xyz_mean, axis=1)
    pcd = pcd[distances <= 0.5]
    xyz_mean = np.mean(pcd[:, :3], axis=0)
    pcd[:, :3] -= xyz_mean

    pcd = uniform_sampling(pcd, 9000)

    return pcd

def uniform_sampling(pcd, n_samples):
    index = np.random.choice(np.arange(0, pcd.shape[0]), size=n_samples, replace=False)
    pcd = pcd[index]

    return pcd

def fps(pcd, n_samples):
    '''
        pcd B N 3
        n_samples int
    '''
    points = pcd[None, :, :3]
    points = torch.tensor(points).cuda()
    fps_idx = pointnet2_utils.furthest_point_sample(points, n_samples) 
    fps_data = pointnet2_utils.gather_operation(points.transpose(1, 2).contiguous(), fps_idx).transpose(1,2).contiguous()
    fps_idx = fps_idx.squeeze(0).cpu().numpy()
    color = pcd[:, 3:][fps_idx]
    fps_data = fps_data.squeeze(0).cpu().numpy()
    pcd = np.concatenate([fps_data, color], axis=1)

    return pcd

def vis_pose(pose, size=0.03):
    init_mesh = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=[0, 0, 0])
    pose_mesh = init_mesh.transform(pose) # pose: 4*4, [[R, t], [0, 0, 0, 1]]

    return pose_mesh

def vis_flow(points, flow):
    line_set = o3d.geometry.TriangleMesh()
    for i in range(flow.shape[0]):
        start = points[i]
        direction = flow[i]

        arrow = o3d.geometry.TriangleMesh.create_arrow(
            cylinder_radius=0.0003, 
            cone_radius=0.0005, 
            cone_height=0.0005, 
            cylinder_height=np.linalg.norm(direction) * 5
        )
        
        # 设置箭头的位置
        arrow.translate(start)
        
        if np.linalg.norm(direction) > 0:
            direction_normalized = direction / np.linalg.norm(direction)
            angle = np.arccos(direction_normalized[2])
            axis = np.cross(np.array([0, 0, 1]), direction_normalized)
            if np.linalg.norm(axis) > 1e-6:
                axis /= np.linalg.norm(axis)
                arrow.rotate(arrow.get_rotation_matrix_from_axis_angle(axis * angle), center=arrow.get_center())
        
        arrow.paint_uniform_color([0, 1, 0])
        line_set += arrow

    return line_set

def generate_raw_data(data_list, save_path, vis=True):
    save_vis = save_path + '_vis'
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(save_vis, exist_ok=True)
    for data_path in tqdm(data_list, desc='Processing files'):
        data = torch.load(data_path)
        save_data_name = data_path.split('/')[-1].replace('.pt', '.pickle')
        save_traj_path = os.path.join(save_path, save_data_name)
        save_vis_name = data_path.split('/')[-1].replace('.pt', '')
        save_traj_vis = os.path.join(save_vis, save_vis_name)
        os.makedirs(save_traj_vis, exist_ok=True)

        trajectory = data['trajectory']
        episode_data = dict()
        pcd_list = []
        image_list = []
        depth_list = []
        action_list = []
        tac_flow_list = []
        tac_pos_list = []
        frame_id = 0



        for frame in trajectory:
            if frame_id == 0:
                frame_id += 1
                continue

            # generate action observation
            classes = frame['observation']['gt_direction']
            if classes < 0:
                classes = 0
            cam_pos = frame['observation']['cam_pose_position']
            offset = frame['observation']['gt_offset']
            rel_action = frame['action']
            current_theta_rad = (offset[2] * np.pi / 180)
            action_x = rel_action[:2] @ [math.cos(current_theta_rad), -math.sin(current_theta_rad)]
            action_y = rel_action[:2] @ [math.sin(current_theta_rad), math.cos(current_theta_rad)]
            abs_action = np.array([action_x, action_y, rel_action[2], rel_action[3]])
            l_init = frame['observation']['world_marker_flow_l'][0]
            r_init = frame['observation']['world_marker_flow_r'][0]
            l_flow = frame['observation']['world_marker_flow_l'][1] - frame['observation']['world_marker_flow_l'][0]
            r_flow = frame['observation']['world_marker_flow_r'][1] - frame['observation']['world_marker_flow_r'][0]
            tac_flow = np.concatenate((l_flow[None, :, :], r_flow[None, :, :]), axis=0)
            tac_pos = np.concatenate((l_init[None, :, :], r_init[None, :, :]), axis=0)

            # generate vision observation
            image = frame['observation']['rgb_picture']
            depth = frame['observation']['depth_picture']
            mask1 = cv2.inRange(image, (255, 255, 255), (255, 255, 255))
            mask = (mask1 == 0) & (depth > 0)
            pcd = get_pcd_from_rgbd(depth, image, mask)
            theta = np.radians(53.75)
            cam_rot = np.array([[np.cos(theta),0,np.sin(theta)], [0,1,0], [-np.sin(theta),0,np.cos(theta)]]) @ np.array([[0,-1,0], [-1,0,0], [0,0,-1]])
            cam_pose = np.eye(4)
            cam_pose[:3, :3] = cam_rot
            cam_pose[:3, 3] = cam_pos
            pcd = transform_pcd(pcd, cam_pose)
            pcd_mask = (pcd[:, 0] > -0.08) & (pcd[:, 0] < 0.08) & (pcd[:, 2] < 0.1)
            pcd = pcd[pcd_mask]
            # pcd = uniform_sampling(pcd, 8192)
            pcd = fps(pcd, 5000)

            # save
            image_list.append(image[None, :, :, :])
            depth_list.append(depth[None, :, :])
            pcd_list.append(pcd[None, :, :])
            action_list.append(abs_action[None, :])
            tac_flow_list.append(tac_flow[None, :, :])
            tac_pos_list.append(tac_pos[None, :, :])

            if vis:            
                flow_l_vis = vis_flow(l_init, l_flow)
                flow_r_vis = vis_flow(r_init, r_flow)
                pcd_vis = o3d.geometry.PointCloud()
                pcd_vis.points = o3d.utility.Vector3dVector(pcd[:, :3])
                pcd_vis.colors = o3d.utility.Vector3dVector(pcd[:, 3:] / 255.0)
                save_pcd_vis = os.path.join(save_traj_vis, str("%03d"%frame_id) + '_pcd.ply')
                save_tac_l_vis = os.path.join(save_traj_vis, str("%03d"%frame_id) + '_tac_l.ply')
                save_tac_r_vis = os.path.join(save_traj_vis, str("%03d"%frame_id) + '_tac_r.ply')
                o3d.io.write_point_cloud(save_pcd_vis, pcd_vis)
                o3d.io.write_triangle_mesh(save_tac_l_vis, flow_l_vis)
                o3d.io.write_triangle_mesh(save_tac_r_vis, flow_r_vis)
            
            frame_id += 1
        
        episode_data['peg_cls'] = int(classes)
        episode_data['points'] = np.concatenate(pcd_list, axis=0)
        episode_data['image'] = np.concatenate(image_list, axis=0)
        episode_data['depth'] = np.concatenate(depth_list, axis=0)
        episode_data['action'] = np.concatenate(action_list, axis=0)
        episode_data['tac_flow'] = np.concatenate(tac_flow_list, axis=0)
        episode_data['tac_pos'] = np.concatenate(tac_pos_list, axis=0)
        
        with open(save_traj_path, 'wb') as f:
            pickle.dump(episode_data, f)
        
    print('End processing')


if __name__ == '__main__':
    data_dir = '/data/zyp/Embodied/vitac_trajs/seed2'
    save_path = '/data/zyp/Embodied/ManiSkill-ViTac2025/data/success_traj/raw_data'
    data_list = get_pt_files(data_dir)
    generate_raw_data(data_list, save_path, vis=True)

    print('end')
    