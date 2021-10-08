import torch
from torch.distributions import Categorical

def environment(coalition, action):
    batch_size = coalition.size(0)

    action =  action - 1

    idx = (coalition != -1).long().sum(dim=1)
    invalid_idx = (idx == coalition.size(1))
    idx[invalid_idx] = -1

    new_coalition = coalition.detach().clone()
    new_coalition[range(batch_size), idx] = action

    is_terminal = torch.logical_or(action == -1, (new_coalition != -1).all(dim=1)) 

    return new_coalition, is_terminal

class MCTS:
    def __init__(self, model, device):
        self.model = model
        self.env = environment
        self.device = device

    def _init_root(self, agents, coalition, num_simulations):
        batch_size, action_size = agents.size(0), 1 + agents.size(1)
        tree_size = 1 + num_simulations
   
        self.batch_idx = torch.arange(batch_size, dtype=torch.long)

        self.parent = torch.zeros(batch_size, tree_size, dtype=torch.long)
        self.action = torch.zeros(batch_size, tree_size, dtype=torch.long)
        self.N = torch.zeros(batch_size, tree_size, dtype=torch.float)
    
        self.children = torch.empty(batch_size, tree_size, action_size, dtype=torch.long).fill_(-1)
        self.children_Q = torch.zeros(batch_size, tree_size, action_size, dtype=torch.float)
        self.children_N = torch.zeros(batch_size, tree_size, action_size, dtype=torch.long)
        self.children_p = torch.zeros(batch_size, tree_size, action_size, dtype=torch.float)

        self.agents = agents
        self.coalition = torch.empty(batch_size, tree_size, coalition.size(1), dtype=torch.long, device=agents.device)

        root = torch.zeros(batch_size, dtype=torch.long)
        return root

    def _new_node(self, node, coalition, prior):
        self.N[self.batch_idx, node] = 1
        self.children_p[self.batch_idx, node] = prior.cpu()
        self.coalition[self.batch_idx, node] = coalition

    def __call__(self, agents, coalition, deterministic, return_eos, num_simulations, tau=1):
        root = self._init_root(agents, coalition, num_simulations)
        prior, value = self.model(agents, coalition, return_eos)

        self._min_values = value.cpu()
        self._max_values = value.cpu() + 1e-6

        self._new_node(root, coalition, prior)
        for idx in range(num_simulations):
            node, action = self._traverse(root)
            node, reward = self._expand(node, action, idx, return_eos)   
            self._backup(node, reward)
        return self._sample_action(root, tau, deterministic)
    
    def _traverse(self, node):
        while True:
            action = self._ucb_action_select(node)
            next_node = self.children[self.batch_idx, node, action]
            is_leaf = (next_node == -1)
            if is_leaf.all():
                return node, action
            node = torch.where(is_leaf, node, next_node)

    def _ucb_action_select(self, node):
        child_visits = self.children_N[self.batch_idx, node, :]
        child_value = self.children_Q[self.batch_idx, node, :] / child_visits
        child_prior = self.children_p[self.batch_idx, node, :]
        visits = self.N[self.batch_idx, node].unsqueeze(1)

        child_value = torch.where(child_visits.bool(), child_value, self._min_values.unsqueeze(1))
        child_value = (child_value - self._min_values.unsqueeze(1)) / (self._max_values - self._min_values).unsqueeze(1)
        
        ucb = child_value + (torch.sqrt(visits) / (child_visits + 1)) * child_prior

        return ucb.argmax(dim=1)

    def _expand(self, node, action, idx, return_eos):
        next_node = torch.empty_like(node).fill_(1 + idx)

        coalition = self.coalition[self.batch_idx, node]
        coalition, is_terminal = self.env(coalition, action.to(self.agents.device))
        prior, value = self.model(self.agents, coalition, return_eos)

        self._min_values = torch.minimum(self._min_values, value.cpu())
        self._max_values = torch.maximum(self._max_values, value.cpu())

        reward = value.cpu()

        self.children[self.batch_idx, node, action] = next_node        
        self._new_node(next_node, coalition, prior)
        self.parent[self.batch_idx, next_node] = node
        self.action[self.batch_idx, next_node] = action

        return next_node, reward

    def _backup(self, node, reward):
        while True:
            node_is_root = (node == 0)
            if node_is_root.all():
                break
            
            parent = self.parent[self.batch_idx, node]

            parent_is_root = (parent == 0)
            mask = 1 - torch.logical_and(node_is_root, parent_is_root).long()

            self.N[self.batch_idx, parent] += mask
            action = self.action[self.batch_idx, node]
            self.children_N[self.batch_idx, parent, action] += mask
            self.children_Q[self.batch_idx, parent, action] += mask * reward

            node = parent

    def _sample_action(self, node, tau, deterministic):
        child_visits = self.children_N[self.batch_idx, node, :]

        probs = child_visits ** tau
        probs = probs / probs.sum(dim=1, keepdim=True)

        if deterministic:
            action = torch.argmax(probs, dim=1)
        else:
            distribution = Categorical(probs)
            action = distribution.sample()

        return action, probs
