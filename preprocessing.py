
# coding: utf-8

# In[ ]:


#ツイートデータを学習用に整形
#preprocessing.py

import MeCab
import re
import pandas as pd
import pprint
import emoji
import neologdn
import urllib.request
import unicodedata
import string

class For_Model():
    
    def __init__(self):
        self.mecab = MeCab.Tagger("-Owakati")
        self.data = './output/buzz_tweet.csv' #取得したデータのパス
        self.columns = ["Followers", "Full_text","Posi_score", "Nega_score","Judge"] #取得したい列名
        self.out_file = "train_buzz.txt" #出力ファイル名
        self.mode = 'w' #学習データの保存モード　'a'：追加／'w'：上書き
        self.text = "Full_text" #ツイートテキストの列を指定
        similar = str(input("ツイート予定文書を入力してください\n"))
        self.similar = str(similar)

    #データを読み込む
    def Load_tweets(self): 
        print("前処理中です…")
        df = pd.read_csv(self.data, usecols = self.columns)
        print("読み込んだツイート数", len(df))
        
        #英字・記号等を除くと4０w以下になるtweetは削除(テキストデータに変更は加えない)
        index = []
        for i in range(len(df)):
            line = df.iloc[i] #データフレームから１行ずつ取り出す
            text = str(line["Full_text"]) #さらにツイート文のみ取り出す
            text = re.sub(r'[!-~]', "", text)#半角記号,数字,英字を削除
            text = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
            text = re.sub('http?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
            #line["Full_text"] = text
            if len(text) < 40:
                index.append(i) #ツイート文４０w以下の行のインデックスを保存
        df_tweet = df.drop(df.index[index]) #保存した行は削除
        df_tweet = df_tweet.reset_index(drop=True) #インデックスを振り直す
        
        #判定用テキストをリストの最後に追加
        tweets = []
        for i in df_tweet[self.text]:
            tweets.append(i)
        if self.similar == None:
            pass
        else:
            tweets.append(self.similar)
        return df_tweet, tweets

    def Stop_Words(self):
        # ストップワードをダウンロード
        url = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
        urllib.request.urlretrieve(url, './output/stop_word.txt')

        with open('./output/stop_word.txt', 'r', encoding='utf-8') as file:
            stopwords = [word.replace('\n', '') for word in file.readlines()]

        #追加ストップワードを設定（助詞や意味のない平仮名１文字）
        add_words = ['あ','い','う','え','お','か','き','く','け','こ','さ','し','す','せ','そ','た','ち','つ','て','と',
                     'な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ','ま','み','む','め','も','や','ゆ','よ',
                     'ら','り','る','れ','ろ','わ','を','ん','が','ぎ','ぐ','げ','ご','ざ','じ','ず','ぜ','ぞ',
                     'だ','ぢ','づ','で','ど','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ',
                     'くん','です','ます','ました','そして','でも','だから','だが','くらい','その','それ','かも',
                     'あれ','あの','あっ','そんな','この','これ','とか','とも','する','という','ござい',
                     'ので','なんて','たら', 'られ','たい','さて','てる','ください','なる','けど','でし',
                     'じゃん','だっ','なっ','でしょ', 'ある','って','こんな','ねえ'
                    ]
        stopwords = stopwords + add_words
        return stopwords

    def Tokenizer(self, text, stopwords):

        words = []
        text = self.mecab.parse(text)
        text = text.split(' ')
        for j in range(len(text)):
            if text[j] not in stopwords:
                words.append(text[j])
        return words

    def remove_emoji(self, text):
        return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

    #記号削除
    def format_text(self, text):
        text = unicodedata.normalize("NFKC", text)  # 全角記号を半角へ置換
        # 記号を消し去るための魔法のテーブル作成
        table = str.maketrans("", "", string.punctuation  + "「」、。・*`+-|?#!()\[]<>=~/")
        text = text.translate(table)
        return text

    def main(self):
        tweets_num = 0
        stopwords = self.Stop_Words()
        df_tweet, tweets = self.Load_tweets()
        #ツイートを分かち書きしてcsvに出力(モード'a'はデータ追加、モード'w'は新規作成)
        with open('./output/' + self.out_file, self.mode) as f:
            for i in tweets:
                tweets_num += 1
                i = neologdn.normalize(i)
                i = re.sub('\n', "", i)
                i = re.sub(r'[!-~]', "", i)#半角記号,数字,英字を削除
                i = re.sub(r'[︰-＠]', "", i)#全角記号削除
                i = self.format_text(i)#記号削除
                i = re.sub(r'[【】●ㅅ●Ф☆✩︎♡→←▼①②③④⑤『』ω《》∠∇∩♪∀◞ཀCщ≧≦ ́◤◢■◆★※↑↓〇◯○◎⇒▽◉Θ♫♬〃“”◇ᄉ⊂⊃д°]', "", i)
                #i = re.sub(r'[‥…？！〜「」｢｣:：♪♩『』→↓↑〈〉・゜・´Д´°ω°•ω•★＊☆♡（）✔Θ∀´∀｀˘ω˘‼бωб￣▽￣]', "", i)
                i = self.remove_emoji(i)
                i = self.Tokenizer(i, stopwords)
                i = ' '.join(i) #リストを文字列に変換
                i = str(i)
                f.write(i)

        with open('./output/' + self.out_file) as f:
             wakati = f.read()

        print('csv出力完了：'+ self.out_file)
        print("学習用ツイート数（判定用ツイート含む/短すぎるツイートは削除）：", tweets_num)
        print("[分かち書きサンプル]\n", wakati[:100])
        print()
        return df_tweet, self.similar

