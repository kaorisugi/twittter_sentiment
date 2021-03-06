# 極性判定とDoc２Vecを使ったTwitterネガポジ予測

## ※実行結果とコードは　twitter_judgement_model.ipynb　にて参照ください

### 【このnotebookについて】
2019年7〜10月までフルタイムで通っていたスクールの卒業課題テーマを、機械学習の勉強のために発展させたものです<br>
卒業発表スライド　https://www.slideshare.net/secret/y0m7g1nZdxpVYP<br>
＊当初は炎上予測がテーマだったので、このnotebookの内容とはややズレます<br>
＊表紙スライドの字が見えない場合は２枚目から戻ると見えます<br>

＊ちなみに…<br>
スクールで取り組んだ課題のリポジトリ https://github.com/kaorisugi/diveintocode-ml<br>
論文読解課題のスライドシェア https://www.slideshare.net/secret/qGmdiwl4uGS20O<br>

### 【ゴール】
これからツイートする予定の文章に対し、過去の類似ツイートを探し、反応のネガポジスコア付きで上位１０位まで提示する。<br>

### 【モデルの仕組み】
１）ツイートデータセットを取得<br>
　・TwitterAPIを使ってツイートを取得<br>
　・各ツイートに対する反応ツイート（リプライ、引用RT）を取得<br>
　・反応ツイートの極性表現数をカウントしてネガポジスコアとpositive/negative/fire!!!判定を得る<br>
　（positive/negativeの判定基準：極性表現数が多い方、fire!!!(炎上）の判定基準：極性表現の７０％以上がnegative）<br>
２）データセットの前処理<br>
　・正規表現、ストップワード除去など<br>
３）予測モデルを生成<br>
　・データセットをDoc２vecで学習<br>
４）ツイート予定文章のネガポジ予測を返す<br>
　・データセットから、ツイート予定文書と似ている文書を探す<br>
　・ネガポジスコア付きで、類似ツイート上位１０個を返す<br>

### 【結果】
類似度確認用にデータセット内にあるものと同じ文を入力したところ、類似度1位で返ってきた。また、２位、３位にもマスクに関する似た話題のツイートが提示されたので類似ツイートの抽出は成功。ネガポジスコアもデータズレなどなく正確に表示され、目的は達成できた。<br>
ツイッターAPI制限により、まだサンプルが少ない（完成時２００件程度）が、データを蓄積できる仕様にしているので、ツイート文のバリエーションを増やしていけば、様々な入力文に対応できるようになると思う。<br>
ネガポジ判定については、ネガティブなテーマへの言及に共感したコメントでネガ判定が出ているケースも多く、必ずしもツイート主へのネガ感情ではないことに注意が必要。<br>

### 【その他試みたこと】
１）文章ベクトルを特徴量としたネガポジ予測モデル<br>
　・文章ベクトルとフォロワー数を特徴量X、ネガポジスコアを目的変数yとしたデータを学習<br>
　・文章ベクトルはDoc２vecとTf-idfの２種を作成<br>
　・ツイート予定文書を入力してネガポジスコアを予測する<br>
　・試した予測モデル<br>
　・MultiOutputRegressor、SVRのrbf と　SVRの線形、lightgbm、ランダムフォレスト<br>
　 　→精度が低すぎて断念<br>
２）ツイッターAPI制限への挑戦（データセットの拡大）<br>
　・古いツイートを大量取得できるパッケージを発見（通常は１週間程度しか遡れない）<br>
　　　→取得データから反応ツイートの取得を試みたができなかった<br>

### 【利用するには】
・config.py ファイルにツイッターAPIトークンを記入<br>
・jupyternotebookファイル　twitter_judgement_model.ipynbを実行<br>
・jupyternotebook上でのMeCab利用で詰まる場合は、下記の自然言語処理環境のDockerイメージを使うとうまくいきました。<br>
https://github.com/hoto17296/docker-japanese-nlp<br>

### Requirement
・必要なツール、ライブラリ<br>
$ pip install tweepy<br>
$ pip install oseti<br>
$ pip install requests requests_oauthlib<br>
$ pip install sengiri<br>
$ pip install gensim<br>
$ pip install emoji<br>
