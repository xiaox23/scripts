import numpy as np
from scipy.spatial.transform import Rotation as R

def get_h2w(euler, xyz):
    '''
    input:
        euler: rpy of eef pose (unit: rad)
        xyz: eef position (unit: mm)
    output:
        h2w: hand to world transform
    '''
    r = R.from_euler('xyz', euler)
    h2w = np.eye(4)
    h2w[:3, :3] = r.as_matrix()
    h2w[:3, 3] = xyz
    return h2w

def calibrate_c2h(camera_depth):
    '''
    input:
        camera_depth: distance from rgb sensor to camera bottom (unit: mm)
    output:
        c2h: camera to hand transform
    '''
    tx = 110.055 - camera_depth * np.cos(np.radians(53.75))
    ty = 20.0
    tz = 14.253 + camera_depth * np.sin(np.radians(53.75))
    translation = np.array([tx, ty, tz])

    theta1 = np.radians(37.5)
    theta3 = np.radians(45)
    rotation = np.array([[0, -1, 0],
                         [1, 0, 0],
                         [0, 0, 1]]) @ \
               np.array([[np.cos(theta1), 0, -np.sin(theta1)], 
                         [0, 1, 0], 
                         [np.sin(theta1), 0, np.cos(theta1)]])
    transform_1 = np.eye(4)
    transform_1[:3, :3] = rotation
    transform_1[:3, 3] = translation

    rotation_2 = np.array([[np.cos(theta3), -np.sin(theta3), 0], 
                           [np.sin(theta3), np.cos(theta3), 0], 
                           [0, 0, 1]])
    transform_2 = np.eye(4)
    transform_2[:3, :3] = rotation_2

    transform = transform_2 @ transform_1

    return transform

def calbirate_t2h(x):
    '''
    input:
        x: gripper position (open=0, close≈50, unit: mm)
    output:
        t2h: [left_tactile, right_tactile] to hand transform
    '''
    translation_l = np.array([57.55-x, 0, 168.25+12.5])
    translation_r = np.array([x-57.55, 0, 168.25+12.5])
    rotation_l = np.array([[ 0,  0,  1], 
                           [ 0,  1,  0], 
                           [-1,  0,  0]])
    rotation_r = np.array([[ 0,  0,  1], 
                           [ 0, -1,  0], 
                           [ 1,  0,  0]])

    theta = np.radians(45)
    rotation = np.array([[np.cos(theta), -np.sin(theta), 0], 
                           [np.sin(theta), np.cos(theta), 0], 
                           [0, 0, 1]])
    transform = np.eye(4)
    transform[:3, :3] = rotation

    transform_l = np.eye(4)
    transform_l[:3, :3] = rotation_l
    transform_l[:3, 3] = translation_l
    transform_l = transform @ transform_l

    transform_r = np.eye(4)
    transform_r[:3, :3] = rotation_r
    transform_r[:3, 3] = translation_r
    transform_r = transform @ transform_r

    return [transform_l, transform_r]

def calibrate_a2w(c2h, t2hs, h2w):
    '''
    input:
        c2h: camera to handd transform
        t2hs: [left_tactile, right_tactile] to hand transform
        h2w: hand to world transform
    output:
        a2w: [camera, left_tactile, right_tactile] to world transform
    '''
    a2w = list()
    c2w = np.dot(h2w, c2h)
    a2w.append(c2w)
    for t2h in t2hs:
        t2w = np.dot(h2w, t2h)
        a2w.append(t2w)

    return a2w



(franka)  robotics@robotics  ~  rostopic echo /device_0/sensor_1/Color_0/info/camera_info
header: 
  seq: 0
  stamp: 
    secs: 0
    nsecs:         0
  frame_id: ''
height: 480
width: 640
distortion_model: "Inverse Brown Conrady"
D: [0.0, 0.0, 0.0, 0.0, 0.0]
K: [604.306884765625, 0.0, 310.15472412109375, 0.0, 604.662353515625, 251.01321411132812, 0.0, 0.0, 1.0]
R: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
P: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
binning_x: 0
binning_y: 0
roi: 
  x_offset: 0
  y_offset: 0
  height: 0
  width: 0
  do_rectify: False

# rgb
fx, fy = 604.306884765625, 604.662353515625  # Focal lengths in x and y
cx, cy = 310.15472412109375, 251.01321411132812  # Principal point (image center)


(franka)  robotics@robotics  ~  rostopic echo /device_0/sensor_0/Depth_0/info/camera_info
header: 
  seq: 0
  stamp: 
    secs: 0
    nsecs:         0
  frame_id: ''
height: 480
width: 640
distortion_model: "Brown Conrady"
D: [0.0, 0.0, 0.0, 0.0, 0.0]
K: [385.4941711425781, 0.0, 317.0605773925781, 0.0, 385.4941711425781, 238.4705047607422, 0.0, 0.0, 1.0]
R: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
P: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
binning_x: 0
binning_y: 0
roi: 
  x_offset: 0
  y_offset: 0
  height: 0
  width: 0
  do_rectify: False

# depth
fx, fy = 385.4941711425781, 385.4941711425781  # Focal lengths in x and y
cx, cy = 317.0605773925781, 238.4705047607422  # Principal point (image center)