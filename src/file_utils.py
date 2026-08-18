"""ファイルの読み書きに関する関数。"""

from io import BytesIO
from pathlib import Path

import pandas as pd


def read_uploaded_file(uploaded_file: object) -> pd.DataFrame:
    """Streamlit でアップロードされた CSV/XLSX を読み込む。"""
    suffix = Path(uploaded_file.name).suffix.lower()  # type: ignore[attr-defined]
    if suffix == ".csv":
        # Excel 由来の CSV でよく使われる UTF-8 BOM にも対応する。
        return pd.read_csv(uploaded_file, encoding="utf-8-sig")
    if suffix == ".xlsx":
        return pd.read_excel(uploaded_file, engine="openpyxl")
    raise ValueError("CSV または .xlsx ファイルを選択してください。")


def to_excel_bytes(dataframe: pd.DataFrame) -> bytes:
    """DataFrame をダウンロード用 Excel バイト列に変換する。"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="cleaned_data")
    return output.getvalue()


def make_download_name(original_name: str) -> str:
    """元ファイル名から「_cleaned.xlsx」付きの名前を作る。"""
    return f"{Path(original_name).stem}_cleaned.xlsx"
