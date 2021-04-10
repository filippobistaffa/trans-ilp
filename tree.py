from abc import ABC, abstractmethod
from collections import defaultdict
import random
import math


class MCTS:
    def __init__(self, root, iterations, exploration_rate, uct_weight):
        self.Q = defaultdict(float) # total reward of each node
        self.A = defaultdict(float) # average reward for each node
        self.N = defaultdict(int)   # total visit count for each node
        self.children = dict()      # children of each expanded node
        self.root = root

        # search parameters
        self.exploration_rate = exploration_rate
        self.uct_weight = uct_weight
        self.iterations = iterations

        # simulation statistics
        self.simulations = 0
        self.deadends = 0

    def run(self):
        for _ in range(self.iterations):
            # ---------------------------------------
            # Tree policy:
            # select new leaf node to add to the tree
            # ---------------------------------------
            path = self.tree_policy(self.root)
            #print('Selected path:', path)
            leaf = path[-1]
            self.add_to_tree(leaf)

            # ---------------------------------------
            # Default policy
            # Compute the reward by simulation
            # ---------------------------------------
            reward = self.default_policy(leaf)
            #print('Reward from simulation:', reward)

            # ---------------------------------------
            # Backpropagation
            # ---------------------------------------
            self.backpropagate(path, reward)
        terminal = sorted(filter(lambda item: item[0].is_terminal(), self.A.items()), key=lambda item: item[1])
        return terminal

    def tree_policy(self, node):
        """
        - select an unexpanded node if no expanded node is present,
          or with a probability of self.exploration_rate
        - select an expanded node with a probability of 1-self.exploration_rate
        - to select among unexpanded nodes (without Q value), use the reward
          or any other guiding heuristic
        - to select among expanded nodes (with a Q value), use UCT
        """

        def select_unexplored(children):
            return max(children, key=lambda x: x.reward())

        def select_uct(children, parent):
            def uct(x):
                import sys
                return self.A[x] + self.uct_weight * math.sqrt(
                    math.log(self.N[parent]) / (self.N[x] + sys.float_info.epsilon)
                )
            return max(children, key=uct)

        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                return path
            unexplored = self.children[node] - self.children.keys()
            explored = [n for n in self.children[node] if n not in unexplored]
            #print('Explored children of {}: {}'.format(node, explored))
            #print('Unexplored children of {}: {}: '.format(node, unexplored))
            if (unexplored and random.random() < self.exploration_rate) or (not explored):
                n = select_unexplored(sorted(unexplored)) # sort to ensure determinism
                #print('Visiting an unexplored children of {}: {}'.format(node, n))
                path.append(n)
                return path
            else:
                node = select_uct(explored, node)
                #print('UCT select:', node)

    def add_to_tree(self, node):
        if node in self.children: # already expanded
            return
        self.children[node] = node.find_children()

    def default_policy(self, node):
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
        if reward is not None:
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
