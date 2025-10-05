#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import re
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler

class ImageCrawlerProcessor:
    def __init__(self):
        self.target = None
        self.kind = None
        self.limit = 10
        self.engine = 'google'

    # オプション抽出
    def parse_options(self):
        parser = ArgumentParser(description="Image crawler processor")
        parser.add_argument('--tgt', type=str, help='specify target to get')
        parser.add_argument('--knd', type=str, help='specify kind to get')
        parser.add_argument('--lim', type=int, default=10, help='optional, specify limit (default: 10)')
        parser.add_argument('--engine', type=str, default='google', 
                          help='search engine (google or bing, default: google)')

        args = parser.parse_args()
        self.target = args.tgt
        self.kind = args.knd
        self.limit = args.lim
        self.engine = args.engine.lower() if args.engine else 'google'

    # メイン
    def main(self):
        if not self.target or not self.kind:
            print("エラー: --tgt と --knd の両方を指定してください")
            print("例: python script.py --tgt cat --knd animal --lim 20 --engine google")
            return

        self._display_info()
        output_path = self._create_output_path()
        self._download_images(output_path)

    # メインでコールされる関数群
    def _display_info(self):
        """検索情報を表示"""
        query = self._create_query()
        print(f"検索エンジン: {self.engine.upper()}")
        print(f"検索キーワード: {query}")
        print(f"ダウンロード枚数: {self.limit}")

    def _create_output_path(self):
        """出力パスを作成"""
        outdir = self._sanitize_dirname(self.target)
        imgdir = self._sanitize_dirname(self.kind)
        output_path = os.path.join(outdir, imgdir)
        print(f"出力先: {output_path}")
        return output_path

    def _download_images(self, output_path):
        """画像をダウンロード"""
        query = self._create_query()
        crawler = self._get_crawler(output_path)
        
        crawler.crawl(
            keyword=query,
            max_num=self.limit,
            min_size=(200, 200),
        )
        
        print(f"ダウンロード完了: {output_path}")

    # サブ関数群
    def _create_query(self):
        """検索クエリを作成"""
        return f"{self.kind} {self.target}"

    def _sanitize_dirname(self, name):
        """ディレクトリ名をサニタイズ（スペースをアンダースコアに変換）"""
        return re.sub(r'\s', '_', name)

    def _get_crawler(self, output_path):
        """検索エンジンに応じたクローラーを取得"""
        if self.engine == 'bing':
            return BingImageCrawler(storage={'root_dir': output_path})
        else:  # デフォルトはGoogle
            return GoogleImageCrawler(storage={'root_dir': output_path})

if __name__ == '__main__':
    processor = ImageCrawlerProcessor()
    processor.parse_options()
    processor.main()