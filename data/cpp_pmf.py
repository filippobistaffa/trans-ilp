import argparse as ap
import json

parser = ap.ArgumentParser()
parser.add_argument('--pool', type=str, help='Original pool (default: pool.json)', default='pool.json')
args = parser.parse_args()

def constexpr_list(list, name, type):
    return 'constexpr array<{}, {}> {} = {{{}}};'.format(type, len(list), name, str(list)[1:-1].replace('\'', '"'))

with open(args.pool) as file:
    string = file.read().rstrip()
    agents = json.loads('[{}]'.format(string[:-1]))

pers_names = ['sn', 'tf', 'ei', 'pj']
pers_idxs = [3, 4, 5, 6]
histogram = [dict(), dict(), dict(), dict()]

for idx, pers_idx in enumerate(pers_idxs):
    for agent in agents:
        value = float(agent[pers_idx])
        if value in histogram[idx]:
            histogram[idx][value] += 1
        else:
            histogram[idx][value] = 1

for idx, personality in enumerate(histogram):
    name = pers_names[idx]
    keys = []
    occurrences = []
    for k, n in personality.items():
        keys.append(k)
        occurrences.append(n)
    print(constexpr_list(keys, '{}_l'.format(name), 'float'));
    print(constexpr_list(occurrences, '{}_n'.format(name), 'float'));

for idx, personality in enumerate(histogram):
    name = pers_names[idx]
    print('auto dist_{} = discrete_distribution<int>({}_n.begin(), {}_n.end());'.format(name, name, name));

for idx, personality in enumerate(histogram):
    name = pers_names[idx]
    print('(ag.profile).{} = {}_l[dist_{}(gen)];'.format(name, name, name));

histogram = dict()
comp_idx = 7

for idx, competence in enumerate(agents[0][comp_idx]):
    name = competence[0]
    for agent in agents:
        value = float(agent[comp_idx][idx][1])
        if name in histogram:
            if value in histogram[name]:
                histogram[name][value] += 1
            else:
                histogram[name][value] = 1
        else:
            histogram[name] = dict()
            histogram[name][value] = 1

print(constexpr_list(list(histogram.keys()), 'competences', 'string_view'));

for idx, competence in enumerate(histogram):
    name = competence.lower()
    keys = []
    occurrences = []
    for k, n in histogram[competence].items():
        keys.append(k)
        occurrences.append(n)
    print(constexpr_list(keys, '{}_l'.format(name), 'float'));
    print(constexpr_list(occurrences, '{}_n'.format(name), 'float'));

print('array<discrete_distribution<int>, {}> comp_dists = {{'.format(len(histogram)))
for idx, competence in enumerate(histogram):
    name = competence.lower()
    print('    discrete_distribution<int>({}_n.begin(), {}_n.end()){}'.format(name, name, ',' if idx != len(histogram) - 1 else ''));
print('};')

print('const array<vector<float>, {}> comp_levels = {{'.format(len(histogram)))
for idx, competence in enumerate(histogram):
    name = competence.lower()
    print('    vector<float>({}_l.begin(), {}_l.end()){}'.format(name, name, ',' if idx != len(histogram) - 1 else ''));
print('};')
