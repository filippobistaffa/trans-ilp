import torch
from parameters import params
from function import characterisic_function as f

MIN_COLLECTIVE_SIZE = params['environment']['min_collective_size']
MAX_COLLECTIVE_SIZE = params['environment']['max_collective_size']
PENALTY = params['environment']['penalty']

class Collective:
    def __init__(self, participants, device):
        self._batch_size = len(participants)
        self._device = device

        self.participants = participants

        self.indices = torch.empty(
            self._batch_size, MAX_COLLECTIVE_SIZE,
            dtype=torch.long, device=self._device
        ).fill_(-1)

        self.is_terminal = torch.zeros(self._batch_size, dtype=torch.bool, device=self._device)

    def add_participant(self, action):
        action = action - 1

        insert_idx = (self.indices != -1).sum(dim=1)
        insert_idx = torch.where((insert_idx < MAX_COLLECTIVE_SIZE - 1) & (~self.is_terminal),
            insert_idx, torch.empty_like(insert_idx).fill_(-1))

        collective = Collective(self.participants, self._device)
        collective.indices = self.indices.clone()
        collective.indices[range(self._batch_size), insert_idx] = torch.where(self.is_terminal, collective.indices[:, -1], action)
        collective.is_terminal = torch.logical_or(action == -1, insert_idx == -1)

        return collective

    def get_reward(self):
        reward = torch.zeros(self._batch_size, dtype=torch.float, device=self._device)

        n = (self.indices != -1).sum(dim=1)
        is_feasible = (MIN_COLLECTIVE_SIZE <= n)  & (n <= MAX_COLLECTIVE_SIZE)
        
        penalty = torch.empty_like(reward).fill_(PENALTY)
        reward = torch.where(is_feasible, reward, penalty)

        compute_reward = is_feasible & self.is_terminal        
        for b, compute in enumerate(compute_reward):
            if compute:
                idx, p = self.indices[b], self.participants[b]
                reward[b] = f(idx.cpu(), p)

        return reward

def get_random_partial_collective(participants, device):
    batch_size = len(participants)
    pool_size = torch.sum((participants != -1).all(dim=-1), dim=-1)

    collective = Collective(participants, device)
    indices = torch.cat([
        torch.randint(s, size=(1, MAX_COLLECTIVE_SIZE), device=device)
        for s in pool_size], dim=0)

    collective_size = torch.randint(MAX_COLLECTIVE_SIZE, size=(batch_size, 1), device=device)
    collective.indices = torch.where(
        torch.arange(MAX_COLLECTIVE_SIZE, device=device).repeat(batch_size, 1) < collective_size,
        indices, collective.indices)

    return collective
