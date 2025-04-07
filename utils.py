"""
このファイルは、画面表示以外の様々な関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import pandas as pd  # （追加）
from typing import List
from sudachipy import tokenizer, dictionary
import constants as ct
from logger import get_logger #logger.pyからget_loggerをインポート(追加)
logger = get_logger(__name__) #logger.pyからget_loggerをインポート(追加)

############################################################
# 関数定義
############################################################

def build_error_message(message):
    """
    エラーメッセージと管理者問い合わせテンプレートの連結

    Args:
        message: 画面上に表示するエラーメッセージ

    Returns:
        エラーメッセージと管理者問い合わせテンプレートの連結テキスト
    """
    return "\n".join([message, ct.COMMON_ERROR_MESSAGE])


def preprocess_func(text):
    """
    形態素解析による日本語の単語分割
    Args:
        text: 単語分割対象のテキスト
    
    Returns:
        単語分割を実施後のテキスト
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    tokenizer_obj = dictionary.Dictionary(dict="full").create()
    mode = tokenizer.Tokenizer.SplitMode.A
    tokens = tokenizer_obj.tokenize(text ,mode)
    words = [token.surface() for token in tokens]
    words = list(set(words))

    return words

def load_product_data(csv_path=ct.RAG_SOURCE_PATH):
    """
    CSVファイルから商品データを読み込む
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"商品CSVを読み込みました（{len(df)}件）")
        return df
    except Exception as e:
        logger.exception(f"CSV読み込みに失敗: {e}")
        return pd.DataFrame()

def get_stock_info(product_name: str, csv_path=ct.RAG_SOURCE_PATH):
    """
    商品名から在庫情報を取得

    Args:
        product_name: 商品名（完全一致）

    Returns:
        在庫情報の辞書 or None
    """
    try:
        df = load_product_data(csv_path)
        if df.empty:
            logger.error("CSVが空です。在庫検索中止。")
            return None

        product = df[df["商品名"] == product_name]

        if product.empty:
            logger.warning(f"商品が見つかりませんでした: {product_name}")
            return None

        record = product.iloc[0]
        stock_info = {
            "商品ID": int(record["商品ID"]),
            "商品名": record["商品名"],
            "価格": int(record["価格"]),
            "在庫数": int(record["在庫数"]),
            "カテゴリ": record["カテゴリ"],
            "メーカー": record["メーカー"]
        }

        logger.info(f"商品情報取得成功: {stock_info}")
        return stock_info

    except Exception as e:
        logger.exception(f"在庫情報取得時にエラー: {e}")
        return None