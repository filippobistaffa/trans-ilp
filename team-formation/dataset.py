import torch
from random import randrange
from torch.utils.data import Dataset
from oracle.oracle import sample_agents

def list2tensor(agents):
    return torch.tensor([
        [a['gender']] +
        list(a['profile'].values()) +
        list(a['competence_level'].values())
    for a in agents])

class RSDataset(Dataset):
    def __init__(self, data, size, pool_size):
        super(RSDataset, self).__init__()
        self.oracle_data = data
        self.participants_binary = [sample_agents(randrange(pool_size[0], pool_size[1]), randrange(999999999)) for _ in range(size)]

        self.participants = [torch.nn.functional.pad(
            list2tensor(p), (0, 0, 0, pool_size[1] - len(p)), value=-1)
            for p in self.participants_binary]

    def __len__(self):
        return len(self.participants)

    def __getitem__(self, idx):
        return {
            'participants': self.participants[idx],
            'idx': idx}
