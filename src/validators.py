"""値の検査・表記統一を行う関数。"""

import re
import unicodedata
from urllib.parse import urlparse


def is_valid_url(value: object) -> bool:
    """http(s) URL で、ホスト名が妥当なら True を返す。"""
    if not isinstance(value, str) or value != value.strip() or " " in value:
        return False
    try:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        # ホスト名は localhost、IP、またはドットを含むドメインを許可する。
        host = parsed.hostname
        return host == "localhost" or bool(re.fullmatch(r"(?:[A-Za-z0-9-]+\.)+[A-Za-z0-9-]+", host)) or bool(
            re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host)
        )
    except ValueError:
        return False


def normalize_phone(value: object) -> object:
    """電話番号を最小限の範囲で整える。数字の追加や削除はしない。"""
    if not isinstance(value, str):
        return value
    normalized = unicodedata.normalize("NFKC", value).strip()
    # NFKC で変換されない代表的なダッシュもハイフンに統一する。
    return normalized.translate(str.maketrans({"−": "-", "—": "-", "―": "-", "–": "-"}))
