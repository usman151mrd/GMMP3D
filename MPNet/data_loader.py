
import torch
import torch.utils.data as data
import os
import pickle
import numpy as np
import nltk
from PIL import Image
import os.path
import random
from torch.autograd import Variable
import torch.nn as nn
import math


# Environment Encoder

class Encoder(nn.Module):
    def __init__(self):
        super(Encoder, self).__init__()
        self.encoder = nn.Sequential(nn.Linear(6000, 512), nn.PReLU(), nn.Linear(512, 256), nn.PReLU(),
                                     nn.Linear(256, 128), nn.PReLU(), nn.Linear(128, 28))

    def forward(self, x):
        x = self.encoder(x)
        return x


# N=number of environments; NP=Number of Paths
def load_dataset(N=100, NP=4000):  # N=100, NP=4000
    Q = Encoder()
    Q.load_state_dict(torch.load('AE/models/cae_encoder.pkl'))
    if torch.cuda.is_available():
        Q.cuda()

    obs_rep = np.zeros((N, 28), dtype=np.float32)
    for i in range(0, N):
        # load obstacle point cloud
        # import os
        # print(os.getcwd())
        #  os.system('pwd')
        temp = np.fromfile('../dataset2/obs_cloud/obc' + str(i) + '.dat')
        temp = temp.reshape(len(temp) // 3, 3)
        obstacles = np.zeros((1, 6000), dtype=np.float32)
        obstacles[0] = temp.flatten()
        inp = torch.from_numpy(obstacles)
        inp = Variable(inp).cuda()
        output = Q(inp)
        output = output.data.cpu()
        obs_rep[i] = output.numpy()


    print("obs_rep shape")

    ## calculating length of the longest trajectory
    max_length = 0
    path_lengths = np.zeros((N, NP), dtype=np.int8)
    for i in range(0, N):
        for j in range(0, NP):
            fname = '../dataset2/e' + str(i) + '/path' + str(j) + '.dat'
            # print("fname : ", fname)
            if os.path.isfile(fname):
                path = np.fromfile(fname)
                path = path.reshape(len(path) // 3, 3)
                path_lengths[i][j] = len(path)
                if len(path) > max_length:
                    max_length = len(path)

    paths = np.zeros((N, NP, max_length, 3), dtype=np.float32)  ## padded paths

    for i in range(0, N):
        for j in range(0, NP):
            fname = '../dataset2/e' + str(i) + '/path' + str(j) + '.dat'
            # print("fname : ", fname)
            if os.path.isfile(fname):
                path = np.fromfile(fname)
                path = path.reshape(len(path) // 3, 3)
                for k in range(0, len(path)):
                    paths[i][j][k] = path[k]

    # print("Path ", path)
    dataset = []
    targets = []
    for i in range(0, N):
        for j in range(0, NP):
            if path_lengths[i][j] > 0:
                for m in range(0, path_lengths[i][j] - 1):
                    data = np.zeros(34, dtype=np.float32)
                    for k in range(0, 28):
                        data[k] = obs_rep[i][k]
                    data[28] = paths[i][j][m][0]
                    data[29] = paths[i][j][m][1]
                    data[30] = paths[i][j][m][2]
                    data[31] = paths[i][j][path_lengths[i][j] - 1][0]
                    data[32] = paths[i][j][path_lengths[i][j] - 1][1]
                    data[33] = paths[i][j][path_lengths[i][j] - 1][2]
                    # print("Data at line 91 ",data)
                    # print("Path at line 92 ", paths[i][j][m + 1])
                    targets.append(paths[i][j][m + 1])
                    dataset.append(data)

    # print("dataset",dataset)
    # print("targets",targets)
    data = list(zip(dataset, targets))
    random.shuffle(data);
    # print("data = ", data)
    dataset, targets = zip(*data)
    return np.asarray(dataset), np.asarray(targets)


# N=number of environments; NP=Number of Paths; s=starting environment no.; sp=starting_path_no
# Unseen_environments==> N=10, NP=2000,s=100, sp=0
# seen_environments==> N=100, NP=200,s=0, sp=4000
def load_test_dataset(N=10, NP=5, s=5, sp=5):
    obc = np.zeros((N, 10, 3), dtype=np.float32)
    temp = np.fromfile('../dataset2/obs.dat')
    obs = temp.reshape(len(temp) // 3, 3)

    temp = np.fromfile('../dataset2/obs_perm2.dat', np.int32)
    perm = temp.reshape(184756, 10)

    ## loading obstacles
    for i in range(0, N):
        for j in range(0, 10):
            for k in range(0, 3):
                obc[i][j][k] = obs[perm[i + s][j]][k]

    Q = Encoder()
    Q.load_state_dict(torch.load('AE/models/cae_encoder.pkl'))
    if torch.cuda.is_available():
        Q.cuda()

    obs_rep = np.zeros((N, 28), dtype=np.float32)
    k = 0
    for i in range(s, s + N):

        temp = np.fromfile('../dataset2/obs_cloud/obc' + str(i) + '.dat')
        temp = temp.reshape(len(temp) // 3, 3)
        obstacles = np.zeros((1, 6000), dtype=np.float32)
        obstacles[0] = temp.flatten()
        inp = torch.from_numpy(obstacles)
        inp = Variable(inp).cuda()
        output = Q(inp)
        output = output.data.cpu()
        obs_rep[k] = output.numpy()
        k = k + 1
    ## calculating length of the longest trajectory
    max_length = 0
    path_lengths = np.zeros((N, NP), dtype=np.int8)
    for i in range(0, N):
        for j in range(0, NP):
            fname = '../dataset2/e' + str(i + s) + '/path' + str(j + sp) + '.dat'
            if os.path.isfile(fname):
                path = np.fromfile(fname)
                path = path.reshape(len(path) // 3, 3)
                path_lengths[i][j] = len(path)
                if len(path) > max_length:
                    max_length = len(path)

    paths = np.zeros((N, NP, max_length, 3), dtype=np.float32)  ## padded paths

    for i in range(0, N):
        for j in range(0, NP):
            fname = '../dataset2/e' + str(i + s) + '/path' + str(j + sp) + '.dat'
            # print(" : "+fname)
            if os.path.isfile(fname):
                path = np.fromfile(fname)
                path = path.reshape(len(path) // 3, 3)
                for k in range(0, len(path)):
                    paths[i][j][k] = path[k]

    return obc, obs_rep, paths, path_lengths