import math
import time
import random

def ucb(c):
    eps = 1e-6
    def _ucb(node):
        return node.best_value + c * math.sqrt(math.log(node.parent.N) / (node.N + eps))
    return _ucb

class Node():
    def __init__(self, state, parent=None, action=None):
        self.state = state

        self.best_state = state
        self.best_value = state.get_value()
        
        self.N = 0
        self.children = []
        self.parent = parent
        self.action = action

class MCTS():
    def __init__(self, state, c):
        self.root = Node(state)
        self.tree_policy = ucb(c)

    def search(self, time_budget):
        start = time.time()
        while time.time() - start < time_budget:
            leaf = self._traverse(self.root)
            best_state = self._rollout(leaf.state)
            self._backup(leaf, best_state)
        return self.root.N

    def _traverse(self, node):
        while node.children:
            node = max(node.children, key=self.tree_policy)
        return self._expand(node)

    def _expand(self, node):
        for action in node.state.get_actions():
            node.children.append(
                Node(node.state.step(action), parent=node, action=action))
        return node

    def _rollout(self, state):
        best_state, best_value = state, state.get_value()
        while (action := self._get_action_random(state)) is not None:
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
        for action in state.get_actions():
            next_state = state.step(action)
            if (value := next_state.get_value()) > best_value:
                best_action, best_value = action, value
        return best_action

    def _get_action_random(self, state):
        if actions := list(state.get_actions()):
            return random.choice(actions)
        return None
