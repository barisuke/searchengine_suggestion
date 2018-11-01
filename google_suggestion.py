import argparse
from time import sleep
from string import ascii_lowercase
from string import digits
import requests
import urllib.parse
import pandas as pd

class GoogleAutoComplete:
    def __init__(self, test_mode=False, recurse_mode=False):
        self.base_url = 'https://www.google.co.jp/complete/search?'\
                        'hl=ja&output=toolbar&ie=utf-8&oe=utf-8&'\
                        'client=firefox&q='
        self.test_mode = test_mode
        self.recurse_mode = recurse_mode
     
    def get_suggest(self, query):
        buf = requests.get(self.base_url +
                           urllib.parse.quote_plus(query)).json()
        suggests = [ph for ph in buf[1]]
        print("query: [{0}]({1})".format(query, len(suggests)))
        for ph in suggests:
            print(" ", ph)
        sleep(0.1)
        return suggests

    def get_suggest_with_one_char(self, query):
        # キーワードそのものの場合のサジェストワード
        ret = self.get_suggest(query)

        # キーワード＋空白の場合のサジェストワード
        ret.extend(self.get_suggest(query + ' '))

        # -rオプションがあればもう1段階 defalut=True
        if self.recurse_mode:
            ret = self.get_uniq(ret)  # 事前に重複を除いておく
            addonelevel = []
            
            
            for ph in ret:
                addonelevel.append(self.get_suggest(ph + ' '))
            ret.append(addonelevel)

        #return self.get_uniq(ret)
        return self.get_uniq(addonelevel)

    # 重複を除く
    def get_uniq(self, arr):
        uniq_ret = []
        for x in arr:
            if x not in uniq_ret:
                uniq_ret.append(x)
        return uniq_ret
         
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phrase", help="調べたい単語")
    parser.add_argument("--recurse", "-r", default = True, action="store_true",
                        help="もう1段階深く取得")
    args = parser.parse_args()
    
    # Google Suggest キーワード取得
    gs = GoogleAutoComplete(test_mode=args.test, recurse_mode=args.recurse)
    ret = gs.get_suggest_with_one_char(args.phrase)


    #ファイルに保存する
    df = pd.DataFrame({})
    df[args.phrase] = ret[0]
    for i,ph in enumerate(ret[1:]):
        df[ret[0][i]] = pd.Series(ph)
    
    # 出力ファイル名を指定
    excel_writer = pd.ExcelWriter('{}市場調査.xlsx'.format(args.phrase))
    df.to_excel(excel_writer=excel_writer, sheet_name='GKW 予測ワード',index=False)

    # 書き出した内容を保存する
    excel_writer.save()
