import torch
from torch import nn
from transformer.model import Actor
from transformer.parameters import params
from torch.distributions import Categorical

def pool2tensor(agents):
    return torch.tensor([[
        [a['gender']] +
        list(a['profile'].values()) +
        list(a['competence_level'].values())
    for a in agents]])

def collective2tensor(collective):
    return torch.tensor([collective + [-1] * (5 - len(collective))], dtype=torch.long)

class Transformer(nn.Module):
    def __init__(self, pth, tau):
        super(Transformer, self).__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor = Actor(
            params['input_size'],
            params['d_model'],
            params['nhead'],
            params['dim_feedforward'],
            params['num_layers']
        )
        self.tau = tau
        self.actor.load_state_dict(torch.load(pth, map_location=self.device))
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
        probs, _ = self.actor(participants, collective, self.tau)
        action = self._sample_action(probs)
        return action.item() - 1
