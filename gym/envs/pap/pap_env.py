import gym
from gym import spaces, logger
from gym.spaces import Discrete
from gym.spaces import seed
from gym.spaces.multi_discrete import MultiDiscrete
import numpy as np
import random
import sys
from PIL import Image
from scipy.misc import imsave
from gym.utils import seeding
from skimage.measure import compare_ssim as ssim
from skimage import data, img_as_float
"""
0 - No guess yet submitted (only after reset)
1 - Guess is lower than the target
2 - Guess is equal to the target
3 - Guess is higher than the target
"""
class PapEnv(gym.Env):
    def __init__(self):
        seed()
        self.seed()
        #self.img = Image.open(r"E:\gym\gym\envs\pap\012.bmp")
        self.img = Image.open(r"E:\gym\gym\envs\pap\012Ori.bmp")
        #self.mask = np.asarray(Image.open(r"E:\gym\gym\envs\pap\012.png"))
        self.mask = np.asarray(Image.open(r"E:\gym\gym\envs\pap\012Ori.png"))
        print(self.mask)

        self.width, self.height = self.img.size

        self.action_space = spaces.Discrete(256)
        self.observation_space = spaces.Discrete(4)

        self.img_array = np.asarray(self.img.convert('L'))

        self.guess_count = 0
        self.guess_max = 100
        self.observation = 0

        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        print("#######",self.guess_count)
        print(action)
        newMaskArray = np.full([self.width, self.height], -1)
        count=  np.array([0,0])
        for i in range(self.width):
            for j in range(self.height):
                if self.img_array[i][j] >= 70:
                    newMaskArray[i][j] = 0
                    count[1] += 1
                else:
                    newMaskArray[i][j] = 255
                    count[0] += 1
        mask_zero_count = np.count_nonzero(self.mask[...,0]==0)

        if count[0] <  mask_zero_count:
            self.observation = 1
        elif count[0] == mask_zero_count:
            self.observation = 2
        else :
            self.observation = 3

        imsave(r"E:\gym\gym\envs\pap\result2.png", newMaskArray)
        reward = ( min(count[0], mask_zero_count) / max(count[0], mask_zero_count)) ** 2
        print(reward)

        self.guess_count += 1
        done = self.guess_count >= self.guess_max

        return self.observation, reward, done, {}

    def reset(self):
        self.guess_count = 0
        self.observation = 0
        return self.observation
