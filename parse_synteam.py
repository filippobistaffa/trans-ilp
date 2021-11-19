import argparse as ap

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('stdout', type=str)
    args = parser.parse_args()

    with open(args.stdout) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        for line in lines:
            if line.startswith('start run'):
                i = line.split()[-1]
                continue
            if line.startswith('value'):
                v = line.split()[1]
                continue
            if line.startswith('total_time'):
                with open('{}.stdout'.format(i), 'w') as f:
                    f.write(v)
