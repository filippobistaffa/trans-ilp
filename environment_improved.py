import numpy as np

class State():
    def __init__(self, agents, value_function, solution=None, values=None):
        self.agents = agents
        self.f = value_function
        self.solution = solution if solution is not None else self._get_initial_state()
        self.values = values if values is not None else self._get_initial_values()

    def _get_initial_state(self):
        return np.arange(len(self.agents))

    def _get_initial_values(self):
        return np.fromiter((self.f([i], self.agents) for i in self.solution), float)

    def get_value(self):
        return np.nansum(self.values)

    def get_actions(self):
        indices, counts = np.unique(self.solution, return_counts=True)
        return {((i, j), c_i + c_j) for j, c_j in zip(indices, counts) for i, c_i in zip(indices, counts) if (j > i and (c_i == 1 or c_j == 1))}

    def get_coalitions(self):
        indices = np.unique(self.solution)
        return [((self.solution == idx).nonzero()[0].tolist(), self.values[idx]) for idx in indices]

    def get_coalition(self, idx):
        return (self.solution == idx).nonzero()[0].tolist()

    def step(self, action):
        state = State(self.agents, self.f, self.solution.copy(), self.values.copy())
        state.solution[self.solution == action[1]] = action[0]
        state.values[action[1]] = np.nan
        state.values[action[0]] = self.f((state.solution == action[0]).nonzero()[0], self.agents)
        return state
