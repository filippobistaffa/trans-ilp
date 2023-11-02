params = {
    'setup': {
        'seed': 10
    },
    'environment': {
        'task': 'task_english',
        'min_collective_size': 5,
        'max_collective_size': 5,
        'penalty': 0
    },
    'model': {
        'input_size': [2] + 4*[0] + 7*[0],
        'd_model': 256,
        'nhead': 8,
        'dim_feedforward': 512,
        'num_layers': 3
    },
    'training': {
        'pool_size': [20, 50],
        'batch_size': 256,
        'train_size': 51200, #51200,
        'eval_size': 6400, #6400,
        'learning_rate': 0.0001, #0.0001,
        'n_epochs': 100,
        'alpha': 0.05
    }
}
