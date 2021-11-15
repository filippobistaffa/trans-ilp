import torch
from torch import nn
from torch.distributions import Categorical
from transformer.model import Actor
from transformer.parameters import params

def pool2tensor(agents):
    return torch.tensor([[
        [a['gender']] +
        list(a['profile'].values()) +
        list(a['competence_level'].values())
    for a in agents]])

def collective2tensor(collective):
    return torch.tensor([collective + [-1] * (5 - len(collective))], dtype=torch.long)

class Transformer(nn.Module):
    def __init__(self, pth):
        super(Transformer, self).__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.actor = Actor(
            input_size=params['input_size'],
            d_model=params['d_model'],
            nhead=params['nhead'],
            dim_feedforward=params['dim_feedforward'],
            num_layers=params['num_layers'], 
            num_categories=params['num_categories'])
            
        if torch.cuda.is_available():
            self.actor.load_state_dict(torch.load(pth))
        else:
            self.actor.load_state_dict(torch.load(pth, map_location=torch.device('cpu')))
        self.actor.to(self.device)

    def _sample_action(self, probs):
        distribution = Categorical(probs)
        action = distribution.sample()
        return action

    @torch.no_grad()
    def forward(self, participants, collective):
        self.actor.eval()

        participants = pool2tensor(participants).to(self.device)
        collective = collective2tensor(collective).to(self.device)

        probs, _ = self.actor(participants, collective)
        action = self._sample_action(probs)

        return action.item() - 1
