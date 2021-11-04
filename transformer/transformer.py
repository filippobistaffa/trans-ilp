import torch
from torch import nn
from transformer.model import Actor
from transformer.parameters import params
from torch.distributions import Categorical

NUM_ZONES = params['num_zones']
NUM_SIMULATIONS = params['num_simulations']
TAU = params['tau']

class Transformer(nn.Module):
    def __init__(self, pth):
        super(Transformer, self).__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor = Actor(
            params['input_size'],
            params['d_model'],
            params['nhead'],
            params['dim_feedforward'],
            params['num_layers'],
            params['num_categories'])
        if torch.cuda.is_available():
            self.actor.load_state_dict(torch.load(pth))
        else:
            self.actor.load_state_dict(torch.load(pth, map_location=torch.device('cpu')))
        self.actor.to(self.device)

    @torch.no_grad()
    def forward(self, agents, coalition, deterministic=True, return_eos=False):
        agents = agents2tensor(agents).to(self.device)
        coalition = coalition2tensor(coalition).to(self.device)
        probs, _ = self.actor(agents, coalition, return_eos)
        if deterministic:
            action = torch.argmax(probs, dim=1)
        else:
            distribution = Categorical(probs)
            action = distribution.sample()
        return action.item() - 1

def agents2tensor(agents):
    agents = [[idx // NUM_ZONES, idx % NUM_ZONES] for idx in agents]
    return torch.tensor([agents], dtype=torch.long)

def coalition2tensor(coalition):
    return torch.tensor([coalition + [-1] * (5 - len(coalition))], dtype=torch.long)
