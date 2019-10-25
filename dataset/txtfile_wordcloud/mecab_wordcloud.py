#! /usr/bin/python3
#
#   mecab_wordcloud.py
#
#                           Apr/16/2019
# ------------------------------------------------------------------

import sys
print(sys.executable)
import matplotlib
#matplotlib.use('Agg')
matplotlib.use('TKAgg')

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
import MeCab as mc


# ------------------------------------------------------------------
def file_to_str_proc(file_in):
    str_out = ""
    try:
        fp_in = open(file_in,encoding='utf-8')
        str_out = fp_in.read()
        fp_in.close()
    except Exception as ee:
        sys.stderr.write("*** error *** file_to_str_proc ***\n")
        sys.stderr.write(str (ee))
#
    return  str_out
# ------------------------------------------------------------------
def mecab_analysis(text):
    tt = mc.Tagger("-Ochasen")
    tt.parse('')
    node = tt.parseToNode(text)
    output = []
    while node:
        if node.surface != "":  # ヘッダとフッタを除外
            word_type = node.feature.split(",")[0]
            if word_type in ["形容詞", "動詞","名詞", "副詞"]:
                output.append(node.surface)
        node = node.next
        if node is None:
            break
    return output
#
# ------------------------------------------------------------------
def get_wordlist_from_file(file_in):
#
    text_aa = file_to_str_proc(file_in)
    text_bb = text_aa.replace('\n','').replace('\t','')
    rvalue = mecab_analysis(text_bb)
#
    return rvalue
#
# ------------------------------------------------------------------
def create_wordcloud(text,file_png):
    fpath = "./NotoSansCJKjp-Regular.otf"

    # ストップワードの設定
    stop_words = [ 'てる', 'いる', 'なる', 'れる', 'する', 'ある',  \
        'こと', 'これ', 'さん', 'して', \
        'くれる', 'やる', 'くださる', 'そう', 'せる', \
         'した',  '思う',  \
        'それ', 'ここ', 'ちゃん', 'くん', '', \
        'て','に','を','は','の', 'が', 'と', 'た', 'し', 'で', \
        'ない', 'も', 'な', 'い', 'か', 'ので',  \
        'よう', '', 'れ','さ','なっ']

    wordcloud = WordCloud(background_color="black", font_path=fpath,\
        width=1024, height=1024, \
              stopwords=set(stop_words)).generate(text)

    plt.figure(figsize=(6,6))
    plt.imshow(wordcloud)
    plt.axis("off")
#   plt.show()
    plt.savefig(file_png)
#
# ------------------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
file_in = sys.argv[1]
file_png = sys.argv[2]
wordlist = []
try:
    wordlist = get_wordlist_from_file(file_in)
except Exception as ee:
        sys.stderr.write("*** error *** in get_wordlist_from_file ***\n")
        sys.stderr.write(str(ee) + "\n")
#
sys.stderr.write("*** check ccc ***\n")
sys.stderr.write("len(wordlist) = %d \n" % len(wordlist))
try:
    create_wordcloud(" ".join(wordlist),file_png)
except Exception as ee:
        sys.stderr.write("*** error *** in create_wordcloud ***\n")
        sys.stderr.write(str(ee) + "\n")
#
sys.stderr.write("*** 終了 ***\n")
# ------------------------------------------------------------------
