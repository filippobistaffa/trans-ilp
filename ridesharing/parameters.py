params = {
    'setup': {
        'seed': 10
    },
    'environment': {
        'num_zones': 63,
        'min_collective_size': 1,
        'max_collective_size': 5,
        'penalty': -10
    },
    'model': {
        'input_size': [63, 63],
        'd_model': 256,
        'nhead': 8,
        'dim_feedforward': 512,
        'num_layers': 3
    },
    'training': {
        'pool_size': [20, 100],
        'batch_size': 256,
        'train_size': 204800, #204800,
        'eval_size': 25600, #25600,
        'learning_rate': 0.0001,#0.0001,
        'n_epochs': 200,
        'alpha': 0.05
    }
}
