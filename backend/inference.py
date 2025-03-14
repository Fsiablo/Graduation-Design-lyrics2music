from settings import parse_args
import torch
import numpy as np
import json
from model_v2 import VAEmodel
from model_v3 import myBertmodel
from transformers import BertTokenizer
import random
args=parse_args()
def softmax(logits, T=1.):
    e_x = torch.exp(logits / T)
    return e_x / e_x.sum(dim=-1).reshape(-1,args.batch_size,1)
def inference_midi(input_lyrics,seed):
    random.seed(seed)
    T=random.uniform(0,2)
    if seed==0:
        T=1
    batch_size=args.batch_size
    lyrics = []
    for i, lyric in enumerate(input_lyrics.replace('\n', '')):
        if i % batch_size == 0:
            lyrics.append([])
        lyrics[i // batch_size].append(lyric)
    while len(lyrics[-1]) % batch_size != 0:
        lyrics[-1].append('#')

    lyrics = [''.join(i) for i in lyrics]
    tokenizer = BertTokenizer.from_pretrained('static/pretrained_model')
    lyrics = tokenizer(lyrics, truncation=True, padding='max_length', max_length=10, return_tensors='pt',
                            return_length=True)


    params_dict = torch.load('static/Midi_Model/best_model')
    midi_model=myBertmodel(args)
    midi_model.load_state_dict(params_dict)
    midi_model.to('cuda')
    # 设置为评估模式
    midi_model.eval()

    # 模型推理
    out = midi_model(lyrics)

    # 结果转换
    with torch.no_grad():
        results = []
        # print(T)
        # print(out.cpu().numpy())
        # print(softmax(out.cpu().numpy()))
        # print(np.argmax(out.cpu().numpy(), -1).reshape(-1))
        # print(np.argmax(softmax(out.cpu().numpy(),T), -1).reshape(-1))

        # for _ in np.argmax(out.cpu().numpy(), -1).reshape(-1):
        #     results.append(_)
        for _ in torch.topk(softmax(out,T),3,dim=-1)[1].reshape(-1,3):
            index=random.randint(0,2)
            if T!=1:
                if _[0]==0 :
                    results.append(0)
                else:
                    results.append(_[index])
            else:
                results.append(_[0])
    return results

def inference_dur(results):
    midis = []
    args=parse_args()
    batch_size=args.batch_size
    dur_dic = {}
    with open('dur_dic.json', 'r') as f:
        dur_str = f.readline()
        dur_dic = json.loads(dur_str)
    for i, midi in enumerate(results):
        if i % batch_size == 0:
            midis.append([])
        midis[i // batch_size].append(midi) if midi <= 200 else midis[i // batch_size].append(0)
    while len(midis[-1]) % batch_size != 0:
        midis[-1].append(0)
    midis = torch.tensor(midis)

    params_dict = torch.load('static/Duration_Model/best_model')
    dur_model = VAEmodel(args)
    dur_model.load_state_dict(params_dict)
    # 设置为评估模式
    dur_model.eval()

    # 模型推理
    # out = nn.Softmax(dur_model(midis))
    out = dur_model(midis)

    # 结果转换
    with torch.no_grad():
        durations = []
        for _ in np.argmax(out.cpu().numpy(), -1).reshape(-1):
            durations.append(_)

    return durations
