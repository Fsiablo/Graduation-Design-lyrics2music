import torch
def calc_bleu(pred,label):
    cnt=0
    tot=len(label)
    for i in pred:
        if i in label:
            cnt+=1
    return cnt/tot