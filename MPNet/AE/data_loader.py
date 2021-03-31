import torch
import torch.utils.data as data
import os
import pickle
import numpy as np
import nltk
from PIL import Image
import os.path
import random


def load_dataset(N=30000,NP=1800):

	obstacles=np.zeros((N,6000),dtype=np.float32)
	for i in range(4,N):
		temp=np.fromfile('../../dataset2/obs_cloud/obc'+str(i)+'.dat')
		temp=temp.reshape(len(temp)//3,3)
		obstacles[i]=temp.flatten()

	
	return 	obstacles	
