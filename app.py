"""DataCleaner の Streamlit 画面。"""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.cleaner import CleaningOptions, clean_dataframe
from src.file_utils import make_download_name, read_uploaded_file, to_excel_bytes


st.set_page_config(page_title="DataCleaner", page_icon="🧹", layout="wide")
st.title("DataCleaner")
st.subheader("Excel・CSVデータをかんたん整理")
st.caption("元データを上書きせず、選択した項目だけを整理します。")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("ファイルをアップロードすると、ここにプレビューが表示されます。")
    st.stop()

try:
    original_df = read_uploaded_file(uploaded_file)
except (ValueError, UnicodeError, OSError) as error:
    st.error(f"ファイルを読み込めませんでした: {error}")
    st.stop()

st.success(f"「{uploaded_file.name}」を読み込みました（{len(original_df):,} 件）")

with st.expander("整理する内容", expanded=True):
    trim_whitespace = st.checkbox("文字列の前後の空白を削除", value=True)
    remove_duplicates = st.checkbox("完全一致する重複行を検出・削除", value=True)
    detect_blanks = st.checkbox("空欄を検出", value=True)
    check_urls = st.checkbox("URL形式をチェック", value=True)
    normalize_phones = st.checkbox("電話番号表記を整理", value=True)

    columns = list(original_df.columns)
    # 列名から候補を推測し、必要なら画面で変更できるようにする。
    default_url_columns = [c for c in columns if "url" in str(c).lower() or "URL" in str(c)]
    default_phone_columns = [
        c for c in columns if any(word in str(c).lower() for word in ("phone", "tel", "電話"))
    ]
    url_columns = st.multiselect("URLをチェックする列", columns, default=default_url_columns, disabled=not check_urls)
    phone_columns = st.multiselect("電話番号を整理する列", columns, default=default_phone_columns, disabled=not normalize_phones)

options = CleaningOptions(
    trim_whitespace=trim_whitespace,
    remove_duplicates=remove_duplicates,
    detect_blanks=detect_blanks,
    check_urls=check_urls,
    normalize_phones=normalize_phones,
    url_columns=url_columns,
    phone_columns=phone_columns,
)
result = clean_dataframe(original_df, options)

st.markdown("### 集計")
metrics = st.columns(5)
metrics[0].metric("元データ件数", f"{result.original_count:,}")
metrics[1].metric("検出した重複件数", f"{result.duplicate_count:,}")
metrics[2].metric("空欄件数", f"{result.blank_count:,}")
metrics[3].metric("URLエラー件数", f"{result.url_error_count:,}")
metrics[4].metric("整理後データ件数", f"{len(result.cleaned):,}")
st.caption("空欄件数は、空欄の「セル数」です。")

before_tab, after_tab, review_tab = st.tabs(["処理前データ", "処理後データ", "要確認データ"])
with before_tab:
    st.dataframe(original_df, use_container_width=True)
with after_tab:
    st.dataframe(result.cleaned, use_container_width=True)
with review_tab:
    if result.issues.empty:
        st.success("要確認のデータはありません。")
    else:
        st.dataframe(result.issues, use_container_width=True, hide_index=True)

download_name = make_download_name(Path(uploaded_file.name).name)
st.download_button(
    "整理後データをExcelでダウンロード",
    data=to_excel_bytes(result.cleaned),
    file_name=download_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)
