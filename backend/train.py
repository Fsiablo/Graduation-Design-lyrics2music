import torch
from torch import nn
import torch.utils.data as Data
from model_v2 import VAEmodel
from model_v3 import myBertmodel
from settings import parse_args
from DataStorage import DataStorage
from visualdl import LogWriter
from transformers import BertTokenizer,BertModel
import json
import fractions
args=parse_args()
batch_size=args.batch_size
def train_midi():
    log_writer = LogWriter(logdir="./log")
    device=args.device

    global_step = 0

    log_iter = 200
    log_step = 0
    min_loss = 999999999



    net=myBertmodel(args)
    net.train()
    net.to(device)

    optimizer_grouped_parameters = [
        {'params': [p for n, p in net.named_parameters() if 'bert' in n],'lr':1e-5},
        {'params': [p for n, p in net.named_parameters() if 'bert' not in n],'lr' :args.lr}
    ]

    opt=torch.optim.Adam(optimizer_grouped_parameters)
    dt = [i for i in DataStorage().generate(DIGITS=batch_size)]
    valid_dt = dt[-1:]
    dt = dt[:-1]
    for epoch in range(args.epoch_midi):
        for id, data in enumerate(dt):
            # 读取数据
            midis, durations, lyrics = data

            while len(midis[-1]) % batch_size != 0:
                midis[-1].append(0)
            while len(lyrics[-1]) % batch_size != 0:
                lyrics[-1].append('.')

            lyrics = [''.join(i) for i in lyrics]
            tokenizer = BertTokenizer.from_pretrained('static/pretrained_model')
            lyrics_data = tokenizer(lyrics, truncation=True, padding='max_length', max_length=10, return_tensors='pt',
                                    return_length=True)

            labels = torch.tensor(midis)
            # 获取损失值和精确率

            labels=labels.to(device)
            loss, bleu = net(lyrics_data, labels=labels)

            # 清除梯度
            opt.zero_grad()
            # 反向传播
            loss.backward()
            # 使用优化器进行参数优化
            opt.step()
            # 打印训练数据
            if global_step % log_iter == 0:
                print('train epoch:%d step: %d loss:%f bleu:%f' % (
                epoch, global_step, loss.cpu().detach().numpy(), bleu))
                log_writer.add_scalar(tag="train/loss", step=log_step, value=loss.cpu().detach().numpy())
                log_writer.add_scalar(tag="train/acc", step=log_step, value=bleu)
                log_step += 1

                with torch.no_grad():
                    for id, data in enumerate(valid_dt):
                        # 读取数据
                        midis, durations, lyrics = data

                        while len(midis[-1]) % batch_size != 0:
                            midis[-1].append(0)
                        while len(lyrics[-1]) % batch_size != 0:
                            lyrics[-1].append('.')

                        lyrics = [''.join(i) for i in lyrics]
                        tokenizer = BertTokenizer.from_pretrained('static/pretrained_model')
                        lyrics_data = tokenizer(lyrics, truncation=True, padding='max_length', max_length=10,
                                                return_tensors='pt',
                                                return_length=True)

                        labels = torch.tensor(midis)
                        # 获取损失值和精确率

                        labels = labels.to(device)
                        _loss, _bleu = net(lyrics_data, labels=labels)

                print('valid epoch:%d step: %d loss:%f bleu:%f' % (
                    epoch, global_step, _loss.cpu().detach().numpy(), _bleu))
                log_writer.add_scalar(tag="valid/loss", step=log_step, value=_loss.cpu().detach().numpy())
                log_writer.add_scalar(tag="valid/acc", step=log_step, value=_bleu)
                if loss < min_loss:
                    min_loss = loss
                    print('saving the best_model...')
                    # torch.save(net.state_dict(), 'static/Midi_Model/best_model')

            # 全局步数加一
            global_step += 1
    print('saving the final_model...')
    # torch.save(net.state_dict(), 'static/Midi_Model/final_model')
    print('finish...')
def train_dur():
    log_writer = LogWriter(logdir="./log")

    device=args.device
    global_step = 0

    log_iter = 200
    log_step = 0
    min_loss = 999999999

    net=VAEmodel(args)
    net.train()
    net.to(device)
    opt=torch.optim.Adam(lr=args.lr,params=net.parameters())

    dur_dic = {}
    with open('dur_dic.json', 'r') as f:
        dur_str = f.readline()
        dur_dic = json.loads(dur_str)

    for epoch in range(args.epoch_dur):
        dt = [i for i in DataStorage().generate(DIGITS=batch_size)]
        valid_dt = dt[-1:]
        dt = dt[:-1]
        for id, data in enumerate(dt):
            # 读取数据
            midis, durations, lyrics = data

            while len(midis[-1]) % batch_size != 0:
                midis[-1].append(0)
            dur = {v: int(k) for k, v in dur_dic.items()}
            for i in range(len(durations)):
                for j in range(len(durations[i])):
                    if type(durations[i][j]) == fractions.Fraction:
                        durations[i][j] = dur[float(durations[i][j])]
                    else:
                        durations[i][j] = dur[durations[i][j]]
            while len(durations[-1]) % batch_size != 0:
                durations[-1].append(1)

            data = torch.tensor(midis)
            labels = torch.tensor(durations)
            # 获取损失值和精确率
            data=data.to(device)
            labels=labels.to(device)
            loss, acc = net(data, labels=labels)

            # 清除梯度
            opt.zero_grad()
            # 反向传播
            loss.backward()
            # 使用优化器进行参数优化
            opt.step()
            # 打印训练数据
            if global_step % log_iter == 0:
                print('train epoch:%d step: %d loss:%f acc:%f' % (
                epoch, global_step, loss.cpu().detach().numpy(), acc.cpu().detach().numpy()))
                log_writer.add_scalar(tag="train/loss", step=log_step, value=loss.cpu().detach().numpy())
                log_writer.add_scalar(tag="train/acc", step=log_step, value=acc.cpu().detach().numpy())
                log_step += 1

                with torch.no_grad():
                    for id, data in enumerate(valid_dt):
                        # 读取数据
                        midis, durations, lyrics = data

                        while len(midis[-1]) % batch_size != 0:
                            midis[-1].append(0)
                        dur = {v: int(k) for k, v in dur_dic.items()}
                        for i in range(len(durations)):
                            for j in range(len(durations[i])):
                                if type(durations[i][j]) == fractions.Fraction:
                                    durations[i][j] = dur[float(durations[i][j])]
                                else:
                                    durations[i][j] = dur[durations[i][j]]
                        while len(durations[-1]) % batch_size != 0:
                            durations[-1].append(1)

                        data = torch.tensor(midis)
                        labels = torch.tensor(durations)
                        # 获取损失值和精确率
                        data = data.to(device)
                        labels = labels.to(device)
                        _loss, _acc = net(data, labels=labels)

                print('valid epoch:%d step: %d loss:%f acc:%f' % (
                    epoch, global_step, _loss.cpu().detach().numpy(), _acc.cpu().detach().numpy()))
                log_writer.add_scalar(tag="valid/loss", step=log_step, value=_loss.cpu().detach().numpy())
                log_writer.add_scalar(tag="valid/acc", step=log_step, value=_acc.cpu().detach().numpy())
                if loss < min_loss:
                    min_loss = loss
                    print('saving the best_model...')
                    torch.save(net.state_dict(), 'static/Duration_Model/best_model')


            # 全局步数加一
            global_step += 1
    print('saving the final_model...')
    torch.save(net.state_dict(), 'static/Duration_Model/final_model')
    print('finish...')

train_midi()