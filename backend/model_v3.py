import torch
import torch.nn as nn
from settings import parse_args
from transformers import BertTokenizer,BertModel
from utils import calc_bleu
#Encoder+Decoder
class myBertmodel(nn.Module):
    def __init__(self,args):
        super(myBertmodel,self).__init__()
        self.args=args
        self.bert=BertModel.from_pretrained('static/pretrained_model')
        self.fc=nn.Linear(768,args.char_len)
    def forward(self,data, labels=None):
        input_ids = data['input_ids'].to(self.args.device)
        attention_mask = data['attention_mask'].to(self.args.device)
        token_type_ids = data['token_type_ids'].to(self.args.device)
        out=self.bert(input_ids,attention_mask,token_type_ids)
        out=self.fc(out.last_hidden_state)
        # out=torch.softmax(out,-1)
        if labels is not None:
            labels = torch.cuda.LongTensor(labels)
            tmp = out.permute(0, 2, 1)

            labels = labels.squeeze(dim=1)
            loss = nn.functional.cross_entropy(tmp, labels)
            out_t=torch.argmax(out.reshape(-1, self.args.char_len),dim=1)
            label_t=labels.reshape(-1)
            bleu = calc_bleu(out_t,label_t)
            return loss, bleu
        return out
