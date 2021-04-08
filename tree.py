from abc import ABC, abstractmethod
from collections import defaultdict
from time import time
import random
import math


class MCTS:
    def __init__(self, root, budget, iterations, exploration_rate, uct_weight):
        self.Q = defaultdict(float) # total reward of each node
        self.A = defaultdict(float) # average reward for each node
        self.N = defaultdict(int)   # total visit count for each node
        self.children = dict()      # children of each expanded node
        self.root = root

        # search parameters
        self.exploration_rate = exploration_rate
        self.uct_weight = uct_weight
        self.iterations = iterations
        self.budget = budget

        # simulation statistics
        self.simulations = 0
        self.deadends = 0

    def run(self):
        iterations = 0
        start_time = time()
        while True:
            path = self.select(self.root)
            leaf = path[-1]
            #print('Selected path:', path)
            #print('Leaf:', leaf)
            self.expand(leaf)
            reward = self.simulate(leaf)
            if reward is not None:
                #print('Reward from simulation:', reward)
                self.backpropagate(path, reward)
            if self.iterations is not None:
                if iterations >= self.iterations:
                    break
            if self.budget is not None:
                if time() - start_time > self.budget:
                    break
            iterations += 1

    def select(self, node):
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored and random.random() < self.exploration_rate:
                #print('Visiting a new node')
                n = sorted(unexplored).pop()
                path.append(n)
                return path
            else:
                node = self.uct_select(node)  # descend a layer deeper
                #print('UCT select:', node)

    def uct_select(self, node):
        def uct(n):
            if self.N[n] == 0:
                u = float('-inf')
            else:
                log_N_vertex = math.log(self.N[node])
                u = self.Q[n] / self.N[n] + self.uct_weight * math.sqrt(
                    log_N_vertex / self.N[n]
                )
            return u
        #print('Children', self.children[node])
        return max(self.children[node], key=uct)

    def expand(self, node):
        if node in self.children: # already expanded
            return
        self.children[node] = node.find_children()

    def simulate(self, node):
        self.simulations += 1
        while True:
            if node is None:
                #print('Deadend')
                self.deadends += 1
                return None
            #else:
                #print('Simulating from', node)
            if node.is_terminal():
                reward = node.reward()
                return reward
            node = node.find_random_child()

    def backpropagate(self, path, reward):
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            self.A[node] = self.Q[node] / self.N[node]


class Node(ABC):
    @abstractmethod
    def find_children(self):
        return []

    @abstractmethod
    def find_random_child(self):
        return None

    @abstractmethod
    def is_terminal(self):
        return True

    @abstractmethod
    def reward(self):
        return 0

    @abstractmethod
    def __lt__(self, other):
        return True
