import torch
import random
from model import Transformer
from trainer import Trainer
from parameters import params
from oracle.oracle import OracleData

SEED = params['setup']['seed']

random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic=True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

data = OracleData('./data/' + params['environment']['task'])

model = Transformer(
    input_size=params['model']['input_size'],
    d_model=params['model']['d_model'],
    nhead=params['model']['nhead'],
    dim_feedforward=params['model']['dim_feedforward'],
    num_layers=params['model']['num_layers'])

baseline = Transformer(
    input_size=params['model']['input_size'],
    d_model=params['model']['d_model'],
    nhead=params['model']['nhead'],
    dim_feedforward=params['model']['dim_feedforward'],
    num_layers=params['model']['num_layers'])

trainer = Trainer(
    model=model,
    baseline=baseline,
    learning_rate=params['training']['learning_rate'],
    batch_size=params['training']['batch_size'],
    device=device)

trainer.train(
    data=data,
    pool_size=params['training']['pool_size'],
    train_size=params['training']['train_size'],
    eval_size=params['training']['eval_size'],
    n_epochs=params['training']['n_epochs'],
    alpha=params['training']['alpha'])
