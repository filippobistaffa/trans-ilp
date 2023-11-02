import torch
from torch.utils.data import Dataset
from random import randrange
from cdft import CDFT
from parameters import params

NUM_ZONES = params['environment']['num_zones']

class RSDataset(Dataset):
    def __init__(self, size, pool_size, from_cdft=False):
        super(RSDataset, self).__init__()
        if from_cdft:
            cdft = CDFT()
            participants = [torch.tensor(
                cdft.sample(randrange(pool_size[0], pool_size[1]), 720), dtype=torch.long#randrange(0, cdft.tsteps)), dtype=torch.long
            ) for _ in range(size)]

            participants = [torch.nn.functional.pad(torch.stack(
                #[torch.div(p,  NUM_ZONES, rounding_mode="floor"), torch.fmod(p, NUM_ZONES)],
                [p // NUM_ZONES, p % NUM_ZONES],
            dim=1), (0, 0, 0, pool_size[1] - p.size(0)), value=-1) for p in participants]

        else:
            participants = [torch.randint(NUM_ZONES, size=(pool_size, 2)) for _ in range(size)]

        self.participants = participants

    def __len__(self):
        return len(self.participants)

    def __getitem__(self, idx):
        return {
            'participants': self.participants[idx]}
