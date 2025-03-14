from music21 import *
import json
from inference import inference_midi,inference_dur
def music_gen(input_lyrics,seed=0):
    print('generating midi....')
    results=inference_midi(input_lyrics,seed)
    print('generating duration....')
    durations=inference_dur(results)
    dur_dic = {}
    print('writing....')
    with open('dur_dic.json', 'r') as f:
        dur_str = f.readline()
        dur_dic = json.loads(dur_str)
        print('finish')

    stream1 = stream.Stream()
    for i, lyric in enumerate(input_lyrics.replace('\n', '')):
        if results[i] != 0:
            n1 = note.Note(results[i])
        else:
            n1 = note.Rest()
        n1.addLyric(lyric)
        n1.duration = duration.Duration(dur_dic[str(durations[i])])
        stream1.append(n1)
    stream1.write("xml", "static/music/out.xml")
    stream1.write('midi', 'static/music/out.midi')