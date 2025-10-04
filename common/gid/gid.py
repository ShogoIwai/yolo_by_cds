from argparse import ArgumentParser
import os
import re
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--tgt', help=':specify target want to get')
    argparser.add_argument('--knd', help=':specify kind want to get')
    argparser.add_argument('--lim', help=':optional, specify limit (default: 10)')
    argparser.add_argument('--engine', help=':search engine (google or bing, default: google)', default='google')
    args = argparser.parse_args()
    if args.knd: opts.update({'knd': args.knd})
    if args.tgt: opts.update({'tgt': args.tgt})
    if args.lim: opts.update({'lim': args.lim})
    if args.engine: opts.update({'engine': args.engine.lower()})

def main(limit=10):
    query = f"{opts['knd']} {opts['tgt']}"
    outdir = re.sub(r'\s', '_', opts['tgt'])
    imgdir = re.sub(r'\s', '_', opts['knd'])
    output_path = os.path.join(outdir, imgdir)
    
    engine = opts.get('engine', 'google')
    
    print(f"検索エンジン: {engine.upper()}")
    print(f"検索キーワード: {query}")
    print(f"出力先: {output_path}")
    print(f"ダウンロード枚数: {limit}")
    
    # 検索エンジンの選択
    if engine == 'bing':
        crawler = BingImageCrawler(
            storage={'root_dir': output_path}
        )
    else:  # デフォルトはGoogle
        crawler = GoogleImageCrawler(
            storage={'root_dir': output_path}
        )
    
    crawler.crawl(
        keyword=query,
        max_num=int(limit),
        min_size=(200, 200),  # 最小サイズ（オプション）
    )
    
    print(f"ダウンロード完了: {output_path}")

if __name__ == '__main__':
    parseOptions()
    if opts.get('tgt') and opts.get('knd'):
        if opts.get('lim'):
            main(int(opts['lim']))
        else:
            main()
    else:
        print("エラー: --tgt と --knd の両方を指定してください")
        print("例: python script.py --tgt cat --knd animal --lim 20 --engine google")