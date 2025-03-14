from train import train_midi,train_dur
from music_gen import music_gen
import warnings
import torch
warnings.filterwarnings("ignore")
if __name__=='__main__':
    torch.manual_seed(3407)
    # train_midi()
    # train_dur()
    music_gen('锄禾日当午,汗滴禾下土,谁晓盘中餐,粒粒皆辛苦.',seed=1)