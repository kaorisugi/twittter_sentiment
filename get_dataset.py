
# coding: utf-8

# In[ ]:


#get_dataset.py

import tweepy
import re
import emoji
import oseti
from datetime import datetime, date, timedelta, time
import time
import os
import pandas as pd
import csv
from tqdm import tqdm
import config

class Get_Twitter():

    def __init__(self, reload = True, RT_count = 3000, print_rep = False):
        self.oseti_analyzer = oseti.Analyzer()  #極性判定
        self.CK = config.CONSUMER_KEY
        self.CS = config.CONSUMER_SECRET
        self.AT = config.ACCESS_TOKEN
        self.AS = config.ACCESS_TOKEN_SECRET
        self.ew = "配信スタート ＃キャンペーン　リツイートキャンペーン WWWWWWWWW wwwwwwwwww"
        self.print_cnt = 0
        self.print_rep = print_rep
        self.rt = str(RT_count)
        self.columns = [
            "Id", "Date", "Name", "Full_text",
            "Judge", "Posi_score", "Nega_score", "Followers", "link"
        ]
        self.posi_pd = pd.DataFrame([], columns = self.columns)
        self.nega_pd = pd.DataFrame([], columns = self.columns)
        self.fire_pd = pd.DataFrame([], columns = self.columns)
        self.wait = 0
        self.reload = reload
        day = str(input("ツイートを取得する日付を入力(過去１週間以内/入力形式：YYYY-M-D)："))
        day = datetime.strptime(day, '%Y-%m-%d')
        self.day = day.strftime('%Y-%m-%d')
        #最大2200件のツイートを取得するためのページ
        self.pages = [1,2,3,4,5,6,7,8,9,10,11]
#         similar = str(input("ツイート予定文書を入力してください："))
#         self.similar = similar

    #Api認証
    def _Auth(self):
        auth = tweepy.OAuthHandler(self.CK, self.CS)
        auth.set_access_token(self.AT, self.AS)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        return api

    #出力用ディレクトリとcsvファイルを作成（存在しない場合のみ）
    def Make_Dir(self):
        new_dir_path = 'output'
        try:
            os.makedirs(new_dir_path)
        except FileExistsError:
            pass
        if (os.path.isfile('./output/buzz_tweet.csv')) == False:
            self.posi_pd.to_csv('./output/buzz_tweet.csv', index = False)  

    #絵文字削除
    def _remove_emoji(self, text):
        return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

    #テキストを正規表現処理、絵文字削除
    def _format_text(self, text):
        text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
        text=re.sub('\n', "", text)
        text=re.sub(r'@?[!-~]+', "", text)
        text=self._remove_emoji(text)
        return text
    
    #　日付表記を整える、日本時間に修正
    def _date_format(self, date):
        date = datetime.strptime(str(date), '%a %b %d %H:%M:%S %z %Y')
        date = date + timedelta(hours=9)
        return datetime.strftime(date, '%Y-%m-%d %H:%M')

    #statusデータを変数に代入
    def Status(self, status): 
        self.buzz_id = status._json['id']
        self.buzz_id_str = status._json['id_str']
        self.buzz_name = status._json['user']['screen_name']
        self.buzz_full_text = status._json['full_text']
        self.date = status._json['created_at']
        self.date = self._date_format(self.date)
        self.favo = status._json['favorite_count']
        self.rt_count = status._json['retweet_count']
        api = self._Auth()
        self.followers = status._json['user']['followers_count']
        #self.followers = len(api.followers(status._json['user']['screen_name']))
    
    #除外ワード
    def Exclude_Word(self, text):                        
        if self.ew in str(text):
            print("==========")
            print("除外ワード")
            print()
            return True
        else:
            return False

    #ツイート内にリンクがあれば分割
    def Text_Count(self):
        if re.search("(https://t.co/\w+)", self.buzz_full_text) == None:
            self.link = None
        else:                   
            self.buzz_full_text = re.split("(https://t.co/\w+)", self.buzz_full_text)
            self.link = self.buzz_full_text[1]
            self.buzz_full_text = self.buzz_full_text[0]
        if len(self.buzz_full_text) < 30:
            return True

    #リプライ＋引用RTコメントが100未満のツイートは除外
    def Min_Rep(self):
        reply_texts_rows = []
        if self.rep_cnt + self.RTcomme_cnt > 100:
            reply_texts_rows.append(self.rep_row)
            reply_texts_rows.append(self.rt_row)
            return True
        else:
            return False

    #sentiment_listを一次元にし、ツイートごとの極性表現の総和の辞書にする
    def Get_Senti(self):
        self.sentiment_list = sum(self.sentiment_list, [])#１次元にする
        self.sentiment = dict((key, sum(d[key] for d in self.sentiment_list)) for key in self.sentiment_list[0])

    #バズったツイートを取得(デフォルト：5000RT以上)
    def Get_Buzz(self):
        api = self._Auth()
        try:
            status = api.search(q = 'filter:safe min_retweets:' + self.rt + ' exclude:retweets until:' + self.day,
                    lang ='ja',count =100, tweet_mode = 'extended', result_type = 'recent')# rpp = 100, page = page, 
            return status
        
        #エラー時はスキップして次のツイート取得
        except (ValueError,  KeyError) as e:
            print(e)
            
        #リクエスト回数が上限に達した場合はリセット時間まで待機して継続
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            if self.reload:
                self.wait += 1
                print("==========")
                print('TwitterAPIへのリクエスト回数が上限に達しました。リセット時間まで待機して再取得します')
                print('Wait 15min...')
                print()
                for _ in tqdm(range(15)):
                    time.sleep(60)
            else:
                pass

    def Get_Buzz2(self, next_max_id):
        api = self._Auth()
        try:
            status = api.search(q = 'filter:safe min_retweets:' + self.rt + ' exclude:retweets until:' + self.day,
                    lang ='ja',count =100, max_id = next_max_id, tweet_mode = 'extended', result_type = 'recent')
            return status
            
        #エラー時はスキップして次のツイート取得
        except (ValueError,  KeyError) as e:
            print(e)
        #リクエスト回数が上限に達した場合はリセット時間まで待機して継続
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            if self.reload:
                self.wait += 1
                print("==========")
                print('TwitterAPIへのリクエスト回数が上限に達しました。リセット時間まで待機して再取得します')
                print('Wait 15min...')
                print()
                for _ in tqdm(range(15)):
                    time.sleep(60)
            else:
                pass
    
    #リプライを取得
    def Get_Rep(self):
        api = self._Auth()
        query_reply = '@' + self.buzz_name + ' exclude:retweets'
        self.rep_row = []
        self.sentiment_list = []
        self.rep_cnt =0
        wait_cnt = 0
        try:
            for status_reply in api.search(q=query_reply, lang='ja', count=100):
                if status_reply._json['in_reply_to_status_id_str'] == self.buzz_id_str:
                    row = self._format_text(status_reply._json['text'])
                    #極性判定
                    sentiment_score = self.oseti_analyzer.count_polarity(str(row))#strにする
                    self.sentiment_list.append(sentiment_score)
                    self.rep_row.append(row)
                    self.rep_cnt += 1
                else:
                    pass
        #エラーはスキップして次のツイート取得
        except (ValueError,  KeyError, tweepy.TweepError) as e:
            pass

    # 引用RTを取得
    def Get_RT(self):
        api = self._Auth()
        query_quote = self.buzz_id_str + ' exclude:retweets'
        self.RTcomme_cnt = 0
        self.rt_row = []
        try:
            for status_quote in api.search(q=query_quote, lang='ja', count=100):
                if status_quote._json['id_str'] == self.buzz_id_str:
                    continue
                else:
                    row = self._format_text(status_quote._json['text'])
                #極性判定
                sentiment_score = self.oseti_analyzer.count_polarity(str(row))#strにする
                self.sentiment_list.append(sentiment_score)
                self.rt_row.append(row)
                self.RTcomme_cnt += 1
        #エラーはスキップして次のツイート取得
        except (ValueError,  KeyError, tweepy.TweepError) as e:
            pass      

    #取得したTweetをprint
    def Print(self):
        print("name：", self.buzz_name, "／フォロワー数：", self.followers)
        print("date：", self.date, "／ツイートID：", self.buzz_id_str)
        print("RT数：", self.rt_count, "／favorite数：", self.favo)
        print("リプライ数：", self.rep_cnt, "／RTコメント数(上限１００）：", self.RTcomme_cnt)
        self.print_cnt += 1
        if self.print_rep == True:
            print("リプライ\n", self.rep_row)
            print("RTコメント\n", self.rt_row)
        else:
            pass
        print()

    #センチメント判定結果を取得
    def Get_Analysis(self):        
        total = self.sentiment["positive"] + self.sentiment["negative"]
        if self.sentiment["positive"] >= self.sentiment["negative"]:
            if self.print_cnt == 0:
                print("===== 取得したツイートサンプル =====")
                print(self.buzz_full_text)
                print()
                print("【判定:positive】　　極性表現数", self.sentiment)
                self.Print()
            s = pd.Series([self.buzz_id, self.date, self.buzz_name, self.buzz_full_text, "positive", self.sentiment["positive"], self.sentiment["negative"], self.followers, self.link], index = self.columns)
            self.posi_pd = self.posi_pd.append(s, ignore_index=True)
        elif self.sentiment["negative"]/total >= 0.7:
            if self.print_cnt == 0:
                print("===== 取得したツイートサンプル =====")
                print(self.buzz_full_text)
                print()
                print("【判定:fire!!!】　　極性表現数", self.sentiment)
                print("ネガ表現の割合{:.3g}".format(self.sentiment["negative"]/total))
                self.Print()
            s = pd.Series([self.buzz_id, self.date, self.buzz_name, self.buzz_full_text, "fire", self.sentiment["positive"], self.sentiment["negative"], self.followers, self.link], index = self.columns)
            self.fire_pd = self.fire_pd.append(s, ignore_index=True)
        else:
            if self.print_cnt == 0:
                print("===== 取得したツイートサンプル =====")
                print(self.buzz_full_text)
                print()
                print("【判定:negative】　　極性表現数", self.sentiment)
                self.Print()
            s = pd.Series([self.buzz_id, self.date, self.buzz_name, self.buzz_full_text, "negative", self.sentiment["positive"], self.sentiment["negative"], self.followers, self.link], index = self.columns)
            self.nega_pd = self.nega_pd.append(s, ignore_index=True)

    def main(self):
        self.Make_Dir() # データ格納ファイルの準備
        print('検索ページ1のツイートを取得中...')
        tweet_data = self.Get_Buzz()
        for tweet in tweet_data:
            self.Status(tweet)
            if self.wait == 10:
                print("10回待機したため終了")
                break
            if self.Exclude_Word(self.buzz_full_text) == True:# 除外ワードを含むツイートは除外
                continue
            if self.Text_Count() == True: #30W以下のツイートは除外
                continue
            self.Get_Rep() #リプライを取得
            self.Get_RT() #RTコメントを取得
            if self.Min_Rep() == False: # コメントが少ないツイートは除外
                continue
            self.Get_Senti() #コメントをセンチメント判定
            self.Get_Analysis() #ツイートをセンチメント判定
        next_max_id = int(tweet_data[-1].id) - 1
        #print("next_max_id", next_max_id )
        
        for i in range(2, 11):
            print('検索ページ' + str(i) + 'のツイートを取得中...')
            tweet_data = self.Get_Buzz2(next_max_id)

            for tweet in tweet_data:
                self.Status(tweet)
                if self.wait == 10:
                    print("10回待機したため終了")
                    break
                if self.Exclude_Word(self.buzz_full_text) == True:# 除外ワードを含むツイートは除外
                    continue
                if self.Text_Count() == True: #30W以下のツイートは除外
                    continue
                self.Get_Rep() #リプライを取得
                self.Get_RT() #RTコメントを取得
                if self.Min_Rep() == False: # コメントが少ないツイートは除外
                    continue
                self.Get_Senti() #コメントをセンチメント判定
                self.Get_Analysis() #ツイートをセンチメント判定
                next_max_id = int(tweet.id) - 1
            #print("next_max_id"+ str(i), str(next_max_id))
        
        #生成したデータをprint
        print()
        print("↓↓↓positiveサンプル↓↓↓")
        display(self.posi_pd.head())
        print()            
        print("↓↓↓negativeサンプル↓↓↓")
        display(self.nega_pd.head())
        print()
        print("↓↓↓fire_tweetサンプル↓↓↓")
        display(self.fire_pd.head())
        print()
        print()
        
        #生成したPandasDataFrameをcsvで書き出す
        total_pd = pd.concat([self.posi_pd, self.nega_pd, self.fire_pd], ignore_index=True)
        buzz_old = pd.read_csv('./output/buzz_tweet.csv')
        buzz_new = pd.concat([buzz_old, total_pd])#既存データと連結
        buzz_new.drop_duplicates(subset="Id",inplace=True)#重複ID行を削除            
        buzz_new.to_csv('./output/buzz_tweet.csv', index = False, header = True)
        print("csvへの書き出しが完了しました。新規データ数{}、全データ数：{}".format(len(buzz_new) - len(buzz_old), len(buzz_new)))
        print("サンプルが0件の場合は、15分後に再度実行すると取得できる場合があります。") 
        print()

