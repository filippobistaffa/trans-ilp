import torch

num_pools = 204800
size = 50
mode = 'train'

pools = [torch.cat([
    torch.randint(2, size=(size, 1)),
    2 * torch.rand(size, 4) - 1,
    torch.rand(size, 7)
], dim=1) for _ in range(num_pools)]

def tensor2string(tensor, index):
    bracket = lambda x: '[\"' + x[0] + "\"," + x[1] + "]"

    idx = str(index)
    name = "\"name_" + idx + "\""
    gender = str(tensor[0].long().item())
    sn = str(round(tensor[1].float().item(), 2))
    tf = str(round(tensor[2].float().item(), 2))
    ei = str(round(tensor[3].float().item(), 2))
    pj = str(round(tensor[4].float().item(), 2))
    verbal = str(round(tensor[5].float().item(), 2))
    logic_mathematics = str(round(tensor[6].float().item(), 2))
    visual_spatial = str(round(tensor[7].float().item(), 2))
    kinestecica_corporal = str(round(tensor[8].float().item(), 2))
    musical_rythmic = str(round(tensor[9].float().item(), 2))
    intrapersonal = str(round(tensor[10].float().item(), 2))
    interpersonal = str(round(tensor[11].float().item(), 2))

    return '[' + ','.join([
        idx, name, gender,
        sn, tf, ei, pj,
        '[' + ','.join(map(bracket, [
            ('VERBAL', verbal),
            ('LOGIC_MATHEMATICS', logic_mathematics),
            ('VISUAL_SPATIAL', visual_spatial),
            ('KINESTESICA_CORPORAL', kinestecica_corporal),
            ('MUSICAL_RHYTHMIC', musical_rythmic),
            ('INTRAPERSONAL', intrapersonal),
            ('INTERPERSONAL', interpersonal)
        ])) + ']'
    ]) + '],\n'

for j, participants in enumerate(pools):
    with open('./data/pools/' + mode + '/' + str(j) + '_.json', 'w') as f:
        for i, p in enumerate(participants):
            f.write(tensor2string(p, i))

    with open('./data/pools/' + mode + '/' + str(j) + '.json', 'w') as f:
        for i, p in enumerate(participants):
            if i == 0:
                f.write('[' + tensor2string(p, i))
            elif i == len(participants) - 1:
                f.write(tensor2string(p, i).replace(',\n', ']'))
            else:
                f.write(tensor2string(p, i))
