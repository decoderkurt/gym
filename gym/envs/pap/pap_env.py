import gym
from gym import spaces, logger
from gym.spaces import Discrete
from gym.spaces import seed
from gym.spaces.tuple_space import Tuple
import numpy as np
import random
import sys
from PIL import Image

class PapEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self):
        seed()
        self.img = Image.open(r"E:\gym\gym\envs\pap\012.bmp")
        self.mask = np.asarray(Image.open(r"E:\gym\gym\envs\pap\012.png"))
        self.width, self.height = self.img.size

        self.action_space = Tuple((Discrete(self.width),Discrete(self.height)))
        self.state = 100
        self.max_score  = 0
        #print (np.asarray(zz))
        #zz = (np.random.rand(10, 10, 3)* 255).astype('uint8')
        #print (np.asarray(self.mask))
        #Image.fromarray(zz, mode='L').save(r"E:\gym\gym\envs\pap\result.png")
        #Image.fromarray(np.asarray(self.img), mode='RGB').save(r"E:\gym\gym\envs\pap\result2.png")
        """
        newMaskArray = np.full([self.width, self.height, 3], -1)
        score = 0
        for i in range(self.width):
            for j in range(self.height):
                newMaskArray[i,j] = np.random.randint(0,255)
                if newMaskArray[i,j][0]== self.mask[i,j][0] :
                    score += 1
        if score > self.max_score :
            self.max_score = score
        #print (newMaskArray)
        print(score)
        """

    def step(self, action):
        self.state = self.state - 1
        if self.state <= 0 :
            return {}, self.max_score, True, {}

        newMaskArray = np.full([self.width, self.height, 3], -1)
        score = 0
        for i in range(self.width):
            for j in range(self.height):
                newMaskArray[i,j] = np.random.randint(0,255)
                if newMaskArray[i,j][0]== self.mask[i,j][0] :
                    score += 1
        if score > self.max_score :
            self.max_score = score
            print("max socre updated ", self.max_score)

        #self.take_action(action)
        #self.status = self.env.step()
        #reward = self.get_reward()
        #ob = self.env.getState()
        #episode_over = self.status != hfo_py.IN_GAME
        return {}, self.max_score, False, {}

    def reset(self):
        self.state = np.full([self.width, self.height], 0)
        self.max_score = 0
        self.state = 100
        return self.state

    def render(self, mode='human', close=False):
        pass

    def take_action(self, action):
        pass

    def get_reward(self):
        """ Reward is given for XY. """
        return 0
