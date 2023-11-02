import torch
from scipy import stats
from torch.utils.data import DataLoader
from torch.distributions import Categorical
from dataset import RSDataset
import time
from environment import Collective, get_random_partial_collective

def mean(x):
    return sum(x) / len(x)

class Trainer:
    def __init__(self, model, baseline, learning_rate, batch_size, device):
        self.batch_size = batch_size
        self.device = device

        self.model = model.to(device)
        self.baseline = baseline.to(device)
        self.optim = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

    def _sample_action(self, probs):
        distribution = Categorical(probs)
        action = distribution.sample()
        return action

    @torch.no_grad()
    def _rollout(self, participants, collective, policy, pomo=False):
        policy.eval()
        while True:
            if collective.is_terminal.all():
                return collective.get_reward()
            if pomo and (collective.indices == -1).all():
                probs, _ = policy(participants, collective.indices)
                probs = torch.empty_like(probs).fill_(1)
                probs[:, 0] = 0
                probs = probs / probs.sum(1, keepdim=True)
            else:
                probs, _ = policy(participants, collective.indices)
            action = self._sample_action(probs)
            collective = collective.add_participant(action)

    def _one_sided_paired_ttest(self, batch_size, dataset, model, baseline):
        model.eval()
        baseline.eval()

        model_reward = []
        baseline_reward = []

        for data in DataLoader(dataset, batch_size=batch_size, num_workers=4):
            participants = data['participants'].to(self.device)

            collective = Collective(participants, self.device)
            reward = self._rollout(participants, collective, model)
            model_reward.extend(reward.tolist())

            collective = Collective(participants, self.device)
            reward = self._rollout(participants, collective, baseline)
            baseline_reward.extend(reward.tolist())

        _, p_value = stats.ttest_rel(model_reward, baseline_reward, alternative='greater')
        return p_value, mean(model_reward), mean(baseline_reward)

    def _optimize(self, batch_size, dataset, model):
        model.train()

        cum_entropy = 0
        i = 0
        for data in DataLoader(dataset, batch_size=batch_size, num_workers=4, shuffle=True):
            self.optim.zero_grad()

            participants = data['participants'].to(self.device)
            collective = get_random_partial_collective(participants, self.device)

            probs, v = model(participants, collective.indices)

            distribution = Categorical(probs)
            action = distribution.sample()
            prob = distribution.log_prob(action)
            entropy = distribution.entropy()

            cum_entropy += entropy.mean().item()
            i += 1

            next_collective = collective.add_participant(action)
            model_reward = self._rollout(participants, next_collective, model)
            # model_reward = next_collective.get_reward()

            with torch.no_grad():
                probs, _ = self.baseline(participants, collective.indices)

                distribution = Categorical(probs)
                action = distribution.sample()

                next_collective = collective.add_participant(action)
                baseline_reward = self._rollout(participants, next_collective, self.baseline, pomo=False)
                # baseline_reward = next_collective.get_reward()

            advantage = model_reward - baseline_reward
            loss = - (advantage * prob).mean() + torch.mean((model_reward - v) ** 2) - 0.05 * entropy.mean() #+ torch.mean((model_reward - v) ** 2)

            loss.backward()
            self.optim.step()
            for bp, mp in zip(self.baseline.parameters(), self.model.parameters()):
                bp.data.copy_(0.01 * mp.data + (1 - 0.01) * bp.data)

        #print("Average Training Entropy: {0}".format(cum_entropy / i))

    def train(self, pool_size, train_size, eval_size, n_epochs, alpha):
        print("epoch,t,model_reward,baseline_reward,p_value")
        best = float("-inf")
        for epoch in range(n_epochs):
            start = time.time()

            dataset_train = RSDataset(train_size, pool_size, from_cdft=True)
            dataset_eval = RSDataset(eval_size, pool_size, from_cdft=True)

            self._optimize(self.batch_size, dataset_train, self.model)
            p_value, model_reward, baseline_reward = self._one_sided_paired_ttest(
                self.batch_size, dataset_eval, self.model, self.baseline)

            if model_reward > best:
                best = model_reward
            #if p_value < alpha:
            #    torch.save(self.model.state_dict(), './models/transformer.pth')
            #    self.baseline.load_state_dict(self.model.state_dict())
                torch.save(self.model.state_dict(), './models/transformer.pth')

            print(
                str(epoch) + ',' +
                str((time.time() - start) / 60) + ',' +
                str(model_reward) + ',' +
                str(baseline_reward) + ',' +
                str(p_value))
