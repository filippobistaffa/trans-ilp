import random
import math
import time

eps = 1e-6

def ucb(heur, c):
    vmax = {'value': float('-inf'), 'prior': float('-inf')}
    vmin = {'value': float('inf'), 'prior': float('inf')}

    def _normalize(v, mode):
        return (v - vmin[mode]) / (vmax[mode] - vmin[mode] + eps)

    def _ucb(node):
        nonlocal vmax, vmin

        value_score = node.best_value
        prior_score = heur.prior(node.state, node.action, node.merge_size)
        weight = c * math.sqrt(node.parent.N) / (1 + node.N)

        vmax['value'], vmin['value'] = max(vmax['value'], value_score), min(vmin['value'], value_score)
        vmax['prior'], vmin['prior'] = max(vmax['prior'], prior_score), min(vmin['prior'], prior_score)

        return _normalize(value_score, 'value') + weight * _normalize(prior_score, 'prior')
    
    return _ucb

class CSG_Heuristic():
    def __init__(self, size, k, gamma):
        self.qa = {(i, j): 0 for j in range(size) for i in range(size) if j > i}
        self.na = {(i, j): 0 for j in range(size) for i in range(size) if j > i}
        self.qs = {i: 0 for i in range(1, 1 + size)}
        self.ns = {i: 0 for i in range(1, 1 + size)}

        self.k = k
        self.gamma = gamma

    def prior(self, state, action, size):
        coalition = state.get_coalition(action[0])
        actions = [(i, j) for j in coalition for i in coalition if i < j]
        mean, _ = self._get_combined_stats(actions, size)
        return mean

    def sample(self, state, action, size):
        coalition = state.get_coalition(action[0]) + state.get_coalition(action[1])
        actions = [(i, j) for j in coalition for i in coalition if i < j]
        mean, n = self._get_combined_stats(actions, size)
        return mean + self.k * random.random() / (n + eps)

    def backup(self, state):
        for coalition, v in state.get_coalitions():
            #actions = [(i, j) for j in coalition for i in coalition if i < j]
            #for a in actions:
            #    self.qa[a] += v
            #    self.na[a] += 1
            for s in range(len(coalition), 0, -1):
                self.qs[s] += v
                self.ns[s] += 1
                v = self.gamma * v

    def _get_combined_stats(self, actions, size):
        #m = sum(self.qa[a] / math.sqrt(self.na[a] + eps) for a in actions) + self.qs[size] / math.sqrt(self.ns[size] + eps)
        #n = math.sqrt(sum(self.na[a] for a in actions) + self.ns[size])
        m = self.qs[size] / math.sqrt(self.ns[size] + eps)
        n = self.ns[size]
        return m, n

class Node():
    def __init__(self, state, parent=None, action=None, merge_size=None):
        self.state = state

        self.best_state = state
        self.best_value = state.get_value()
        
        self.N = 0
        self.children = []
        self.parent = parent
        self.action = action
        self.merge_size = merge_size

class MCTS():
    def __init__(self, state, c, k, gamma):
        self.root = Node(state)
        self.heuristic = CSG_Heuristic(len(state.agents), k, gamma)
        self.tree_policy = ucb(self.heuristic, c)

    def search(self, time_budget):
        start = time.time()
        while time.time() - start < time_budget:
            leaf = self._traverse(self.root)
            best_state = self._rollout(leaf.state)
            self._backup(leaf, best_state)
            self.heuristic.backup(best_state)
        return self.root.N

    def _traverse(self, node):
        while node.children:
            node = max(node.children, key=self.tree_policy)
        return self._expand(node)

    def _expand(self, node):
        for action, merge_size in node.state.get_actions():
            node.children.append(
                Node(node.state.step(action), parent=node, action=action, merge_size=merge_size))
        return node

    def _rollout(self, state):
        best_state, best_value = state, state.get_value()
        while (action := self._get_action(state)) is not None:
            state = state.step(action)
            if (value := state.get_value()) > best_value:
                best_state, best_value = state, value
        return best_state

    def _backup(self, node, best_state):
        best_value = best_state.get_value()
        while node is not None:
            if best_value > node.best_value:
                node.best_state = best_state
                node.best_value = best_value
            node.N += 1
            node = node.parent

    def _get_action(self, state):
        best_action, best_value = None, float('-inf')
        for action, merge_size in state.get_actions():
            value = self.heuristic.sample(state, action, merge_size)
            if value > best_value:
                best_action = action
                best_value = value
        return best_action
