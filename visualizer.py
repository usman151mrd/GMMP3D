
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import struct
import numpy as np
import argparse



def main(args):
    # visualize point cloud (obstacles)
    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    obs = []
    temp = np.fromfile(args.obs_file)
    obs.append(temp)
    obs = np.array(obs).astype(np.float32).reshape(-1, 3)
    # plt.scatter(obs[:, 0], obs[:, 1], obs[:, 2], c='blue')
    ax.scatter(obs[:, 0], obs[:, 1], obs[:, 2], c='blue')
    # visualize path
    path = np.loadtxt(args.path_file)
    print(path)
    path = path.reshape(-1, 3)
    path_x = []
    path_y = []
    path_z = []
    for i in range(len(path)):
        path_x.append(path[i][0])
        path_y.append(path[i][1])
        path_z.append(path[i][2])

    # plt.plot(path_x, path_y, path_z, c='r', marker='o')

    ax.plot(path_x, path_y, path_z, c='red', label='parametric curve')
    ax.legend()
    plt.show()


parser = argparse.ArgumentParser()
# for training
parser.add_argument('--obs_file', type=str, default='/home/muhayy/GMMP3D/dataset2/obs_cloud/obc5.dat',
                    help='obstacle point cloud file')
parser.add_argument('--path_file', type=str, default='./results/env_0/path_1.txt', help='path file')

args = parser.parse_args()
print(args)
main(args)
