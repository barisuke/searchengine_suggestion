import argparse
from time import sleep
from string import ascii_lowercase
from string import digits
import requests
import urllib.parse
import pandas as pd
import json
from collections import OrderedDict


class AutoComplete:
    def __init__(self,recurse_mode=True):
        self.base_url = ''
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
        words = self.get_suggest(query+' ')
        # キーワード＋空白の場合のサジェストワード
        addonelevel = OrderedDict()
        # -rオプションがあればもう1段階 defalut=True
        if self.recurse_mode:
            words = self.get_uniq(words)  # 事前に重複を除いておく
            for ph in words:
                recurse_list = self.get_suggest(ph + ' ')
                addonelevel[ph] = self.get_uniq(recurse_list)
        return words,addonelevel

    # 重複を除く
    def get_uniq(self, arr):
        uniq_ret = []
        for x in arr:
            if x not in uniq_ret:
                uniq_ret.append(x)
        return uniq_ret
    
    
class GoogleAutoComplete(AutoComplete):
    def __init__(self,recurse_mode=True):
        self.base_url = 'https://www.google.co.jp/complete/search?'\
                        'hl=ja&output=toolbar&ie=utf-8&oe=utf-8&'\
                        'client=firefox&q='
        self.recurse_mode = recurse_mode
     
class AmazonAutoComplete(AutoComplete):
    def __init__(self,recurse_mode=True):
        self.base_url = 'http://completion.amazon.co.jp/search/complete?mkt=6&method=completion&search-alias=aps&q='
        self.recurse_mode = recurse_mode
        
class RakutenAutoComplete(AutoComplete):
    def __init__(self,recurse_mode=True):
        self.base_url = 'https://api.suggest.search.rakuten.co.jp/suggest?cl=dir&rid=0&sid=0&q='
        self.end_url = "&oe=euc-jp&sl=pm_swg&cb=sample"
        self.recurse_mode = recurse_mode
        
    def get_suggest(self, query):
        
        
        buf = json.loads(requests.get(self.base_url +
                           query+self.end_url).text[7:-1])
        suggests = [ph[0] for ph in buf["result"]]
        print("query: [{0}]({1})".format(query, len(suggests)))
        for ph in suggests:
            print(" ", ph)
        sleep(0.1)
        return suggests


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phrase", help="調べたい単語")
    parser.add_argument("--recurse", "-r", default = True, action="store_true",
                        help="もう1段階深く取得")
    args = parser.parse_args()
    
    
    # Google Suggest ワード取得
    googleSuggest = GoogleAutoComplete(recurse_mode=args.recurse)
    columnWords, arr = googleSuggest.get_suggest_with_one_char(args.phrase)
    #ファイルに保存する
    df = pd.DataFrame({})
    df[args.phrase] = columnWords
    for key,value in arr.items():
        df[key] = pd.Series(value)
    # 出力ファイル名を指定
    excel_writer = pd.ExcelWriter('{}市場調査.xlsx'.format(args.phrase))
    df.to_excel(excel_writer=excel_writer, sheet_name='GKW 予測ワード',index=False)
    
    
    # Amazon Suggest ワード取得
    amazonSuggest = AmazonAutoComplete(recurse_mode=args.recurse)
    columnWords, arr = amazonSuggest.get_suggest_with_one_char(args.phrase)
    #ファイルに保存する
    df2 = pd.DataFrame({})
    df2[args.phrase] = columnWords
    for key, value in arr.items():
        df2[key] = pd.Series(value)
    df2.to_excel(excel_writer=excel_writer, sheet_name='Amazon 予測ワード',index=False)
    
    # Rakuten Suggest　ワード取得
    rakutenSuggest = RakutenAutoComplete(recurse_mode=args.recurse)
    columnWords, arr = rakutenSuggest.get_suggest_with_one_char(args.phrase)
    #ファイルに保存する
    df3 = pd.DataFrame({})
    df3[args.phrase] = columnWords
    for key,  value in arr.items():
        df3[key] = pd.Series(value)
    df3.to_excel(excel_writer=excel_writer, sheet_name='楽天 予測ワード',index=False)
    
    
    # 書き出した内容を保存する
    excel_writer.save() 
