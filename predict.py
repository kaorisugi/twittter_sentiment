
# coding: utf-8

# In[2]:


#predict.py

import numpy as np
import math

#ツイート予定文書と類似している上位10件の文書を出力
def main(m, trainings, similar, df_tweet):
    top10 = m.docvecs.most_similar(len(trainings) - 1)
    #top10 = m.docvecs.most_similar(similar)

    print("============== ツイート予定文 ==============\n")
    print(similar)
    print()
    print("======= 類似ツイート上位１０（全{}ツイート中） =======".format(len(trainings)))
    print()
    print("※類似度0.55未満は表示しない")
    print("※nega/posiスコアは対数変換したフォロワー数で割っています")
    print()
    for i in range(len(top10)):
        score = top10[i]
        index = int(score[0])
        similar_score = score[1]
        tweet = df_tweet["Full_text"]
        judge = df_tweet["Judge"]
        posi_score = df_tweet["Posi_score"]
        nega_score = df_tweet["Nega_score"]
        followers = df_tweet["Followers"]
        if similar_score < 0.55:
            break
        else:
            print("…………　類似ツイート{}位：類似度 {}　…………".format((i+1), math.floor(similar_score*100)/100))
            print()
            print(tweet[index])
            print()
            print("【極性】：", judge[index])
            print("posi_score：",math.floor((float(posi_score[index])/np.log(float(followers[index])))*10)/10, "／", "nega_score：", math.floor((float(nega_score[index])/np.log(float(followers[index])))*10)/10, "／followers：", math.floor(float(followers[index])))
            print()
            print()

