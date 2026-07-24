import torch, sys, json
sys.path.append('D:\\KP\\WebEval')
from model_utils import build_model
cn = json.load(open(r'models\class_names.json'))
sn = json.load(open(r'models\species_names.json'))
m = build_model(len(cn), len(sn))
sd = torch.load(r'models\DenseNet-121 - Final Model.pth', map_location='cpu')
m.load_state_dict(sd, strict=False)
print('Loaded!')
