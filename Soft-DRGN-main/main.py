# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np

a=np.zeros((7,7))
k=0
for i in range(7):
    for j in range(7):
        a[i,j]=k
        k=k+1
print('初始矩阵：\n',a)

init90=np.rot90(a,-1)
print('旋转90的初始矩阵\n',init90)




local_indices_x=[]
local_indices_y=[]

OBS_RANGE = 3
for offset_x in range(-OBS_RANGE, OBS_RANGE):
    for offset_y in range(-OBS_RANGE, OBS_RANGE):
        if (offset_x ** 2 + offset_y ** 2) ** 0.5 <= OBS_RANGE:
            local_indices_x.append(offset_x)
            local_indices_y.append(offset_y)
local_indices_x=np.array(local_indices_x)
local_indices_y=np.array(local_indices_y)
a0 = a[3 + local_indices_x, 3 + local_indices_y]
print('圈初始矩阵：\n',a0)


init_test=init90[3 + local_indices_x, 3 + local_indices_y]
print('旋转后的圈矩阵\n',init_test)

two_d_arr = np.zeros((7, 7))

idx = 0
index_list = []
for offset_x in range(-OBS_RANGE, OBS_RANGE):
    for offset_y in range(-OBS_RANGE, OBS_RANGE):
        if (offset_x ** 2 + offset_y ** 2) ** 0.5 <= OBS_RANGE:
            two_d_arr[3+offset_x, 3+offset_y] = idx
            idx += 1
rotated_arr = np.rot90(two_d_arr, -1)
b0 = rotated_arr[3 + local_indices_x, 3 + local_indices_y]

for offset_x in range(-OBS_RANGE, OBS_RANGE):
    for offset_y in range(-OBS_RANGE, OBS_RANGE):
        if (offset_x ** 2 + offset_y ** 2) ** 0.5 <= OBS_RANGE:
            index_list.append(int(rotated_arr[3+offset_x, 3+offset_y]))
print('旋转映射\n',index_list)


rot_a0 = a0[index_list]
print('旋转映射结果\n',rot_a0)


def trans_action(action, trans_type): #改变action的函数
    if trans_type == 0:
        action_map = [4,3,2,1,0,7,6,5,12,11,10,9,8,15,14,13,16]
    elif trans_type == 1:
        action_map = [0,7,6,5,4,3,2,1,8,15,14,13,12,11,10,9,16]
    elif trans_type == 2:
        action_map = [2,3,4,5,6,7,0,1,10,11,12,13,14,15,8,9,16]
    elif trans_type == 3:
        action_map = [4,5,6,7,0,1,2,3,12,13,14,15,8,9,10,11,16]
    elif trans_type == 4:
        action_map = [6,7,0,1,2,3,4,5,14,15,8,9,10,11,12,13,16]
    else:
        raise Exception("变换类型未实现！\n")
    return action_map[int(action)]

trans_type=2

print(trans_action(1,trans_type))
print(trans_action(2,trans_type))
print(trans_action(3,trans_type))
print(trans_action(4,trans_type))
print(trans_action(5,trans_type))
