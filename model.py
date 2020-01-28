
# coding: utf-8

# In[1]:


#Doc2Vecモデルの学習
#model.py

import os
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

class Model():
    def __init__(self):
        self.f = open('./output/train_buzz.txt','r') #空白で単語を区切り、改行で文書を区切っているテキストデータ
        self.data = './output/buzz_tweet.csv'
        
    def fit(self):
        print("Doc2Vecで学習しています…")
        #１文書ずつ、単語に分割してリストに入れていく[([単語1,単語2,単語3],文書id),...]こんなイメージ
        #words：文書に含まれる単語のリスト（単語の重複あり）
        # tags：文書の識別子（リストで指定．1つの文書に複数のタグを付与できる）
        #fにテキスト データをいれる
        trainings = [TaggedDocument(words = self.data.split(),tags = [i]) for i, self.data in enumerate(self.f)]
        #print("Doc２vec文書ベクトル用モデルに学習させたツイート数",len(trainings))

        #文書ベクトル用ツイートテキストの学習
        model = Doc2Vec(
            documents= trainings,
            dm = 0, #dm=1:dmpv それ以外：DBow
            vector_size=300, #文書ベクトルの次元数
            window=15,
            alpha = 0.018, #学習率
            #min_alpha = 0.001,
            min_count = 0, #出現回数●回以下の単語は無視
            sample = 1e-4,
            negative = 5,
            epochs = 400
        )
#         #文書ベクトル用ツイートテキストの学習
#         model = Doc2Vec(
#             documents= trainings,
#             dm = 0, #dm=1:dmpv それ以外：DBow
#             vector_size=300, #文書ベクトルの次元数
#             window=15,
#             alpha = 0.01, #学習率
#             min_count = 0, #出現回数●回以下の単語は無視
#             sample = 1e-4,
#             workers = 4, 
#             epochs = 1000
#         )
        return model, trainings

    #出力用ディレクトリ作成（存在しない場合のみ）
    def Make_Dir(self):
        new_dir_path = 'model'
        try:
            os.makedirs(new_dir_path)
        except FileExistsError:
            pass

    def main(self):       
        # モデルの学習
        self.Make_Dir()
        model, trainings = self.fit()
        model.save("./model/doc2vec.model")

        # モデルのロード(学習済みモデルが用意してあれば、ここからで良い)
        m = Doc2Vec.load('./model/doc2vec.model')
        print("学習が完了しました")
        return m, trainings


# # 上位２位にいいのがでた
# 
# #文書ベクトル用ツイートテキストの学習
#         model = Doc2Vec(
#             documents= trainings,
#             dm = 0, #dm=1:dmpv それ以外：DBow
#             vector_size=300, #文書ベクトルの次元数
#             window=15,
#             alpha = 0.018, #学習率
#             #min_alpha = 0.001,
#             min_count = 0, #出現回数●回以下の単語は無視
#             sample = 1e-4,
#             negative = 5,
#             epochs = 400
#         )
#         
#         #文書ベクトル用ツイートテキストの学習
#         model = Doc2Vec(
#             documents= trainings,
#             dm = 0, #dm=1:dmpv それ以外：DBow
#             vector_size=300, #文書ベクトルの次元数
#             window=15,
#             alpha = 0.015, #学習率
#             #min_alpha = 0.001,
#             min_count = 0, #出現回数●回以下の単語は無視
#             sample = 1e-4, #3にしてもいいかも
#             negative = 5,
#             epochs = 400
#         )
#         
#         #文書ベクトル用ツイートテキストの学習
#         model = Doc2Vec(
#             documents= trainings,
#             dm = 0, #dm=1:dmpv それ以外：DBow
#             vector_size=300, #文書ベクトルの次元数
#             window=15,
#             alpha = 0.01, #学習率
#             #min_alpha = 0.001,
#             min_count = 0, #出現回数●回以下の単語は無視
#             sample = 1e-3,
#             negative = 5,
#             epochs = 500
#             
#          #文書ベクトル用ツイートテキストの学習
#         model = Doc2Vec(
#             documents= trainings,
#             dm = 0, #dm=1:dmpv それ以外：DBow
#             vector_size=300, #文書ベクトルの次元数
#             window=15,
#             alpha = 0.018, #学習率
#             #min_alpha = 0.005,
#             min_count = 0, #出現回数●回以下の単語は無視
#             sample = 1e-5,
#             negative = 5,
#             epochs = 400
#         )
