"""DataCleaner の Streamlit 画面。"""

from pathlib import Path

import streamlit as st

from src.cleaner import CleaningOptions, clean_dataframe
from src.file_utils import make_download_name, read_uploaded_file, to_excel_bytes


st.set_page_config(page_title="DataCleaner", page_icon="🧹", layout="wide")

with st.container(border=True):
    st.title("🧹 DataCleaner")
    st.subheader("Excel・CSVデータをかんたん整理")
    st.write(
        "CSV / Excelをアップロードすると、重複・空欄・URL・電話番号表記などを"
        "まとめて確認・整理できます。"
    )
    st.caption("元データは上書きせず、整理後のデータをExcelファイルで保存できます。")

st.markdown("### 1. ファイルをアップロード")
st.caption("対応形式：CSV / Excel（.xlsx）")

uploaded_file = st.file_uploader(
    "CSVまたはExcelファイルを選択",
    type=["csv", "xlsx"],
    help="1回に1ファイルをアップロードできます。",
)

if uploaded_file is None:
    st.info("💡 ファイルを選択すると、整理項目とデータのプレビューが表示されます。")
    feature_columns = st.columns(3)
    with feature_columns[0].container(border=True):
        st.markdown("**データを整える**")
        st.caption("前後の空白や電話番号表記を統一")
    with feature_columns[1].container(border=True):
        st.markdown("**問題を見つける**")
        st.caption("重複・空欄・不正なURLを確認")
    with feature_columns[2].container(border=True):
        st.markdown("**Excelで保存する**")
        st.caption("整理後のデータをそのままダウンロード")
    st.stop()

try:
    original_df = read_uploaded_file(uploaded_file)
except (ValueError, UnicodeError, OSError) as error:
    st.error(f"ファイルを読み込めませんでした: {error}")
    st.stop()

st.success(f"✅ 「{uploaded_file.name}」を読み込みました（{len(original_df):,} 件）")

st.markdown("### 2. 整理する内容を選択")
st.caption("必要な処理にチェックを入れてください。選択内容はすぐに結果に反映されます。")

with st.container(border=True):
    option_left, option_right = st.columns(2, gap="large")
    with option_left:
        st.markdown("**データの整理**")
        trim_whitespace = st.checkbox("文字列の前後の空白を削除", value=True)
        remove_duplicates = st.checkbox("完全一致する重複行を検出・削除", value=True)
        normalize_phones = st.checkbox("電話番号表記を整理", value=True)
    with option_right:
        st.markdown("**要確認項目の検出**")
        detect_blanks = st.checkbox("空欄を検出", value=True)
        check_urls = st.checkbox("URL形式をチェック", value=True)

    columns = list(original_df.columns)
    # 列名から候補を推測し、必要なら画面で変更できるようにする。
    default_url_columns = [c for c in columns if "url" in str(c).lower() or "URL" in str(c)]
    default_phone_columns = [
        c for c in columns if any(word in str(c).lower() for word in ("phone", "tel", "電話"))
    ]
    st.divider()
    st.markdown("**対象列の設定**")
    st.caption("列名から候補を自動選択します。必要に応じて変更できます。")
    target_left, target_right = st.columns(2, gap="large")
    with target_left:
        url_columns = st.multiselect(
            "URLをチェックする列",
            columns,
            default=default_url_columns,
            disabled=not check_urls,
        )
    with target_right:
        phone_columns = st.multiselect(
            "電話番号を整理する列",
            columns,
            default=default_phone_columns,
            disabled=not normalize_phones,
        )

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

st.markdown("### 3. 整理結果")
st.caption("選択した処理による検出・整理結果です。")
metrics = st.columns(5)
with metrics[0].container(border=True):
    st.metric("元データ", f"{result.original_count:,} 件")
with metrics[1].container(border=True):
    st.metric("重複", f"{result.duplicate_count:,} 件")
with metrics[2].container(border=True):
    st.metric("空欄", f"{result.blank_count:,} 件")
with metrics[3].container(border=True):
    st.metric("URLエラー", f"{result.url_error_count:,} 件")
with metrics[4].container(border=True):
    st.metric("整理後データ", f"{len(result.cleaned):,} 件")
st.caption("空欄件数は、空欄の「セル数」です。")

before_tab, after_tab, review_tab = st.tabs(["📄 処理前データ", "✨ 処理後データ", "⚠️ 要確認データ"])
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
st.markdown("### 4. 整理後データを保存")
with st.container(border=True):
    st.write("**確認が完了したら、整理後のデータをExcel形式で保存できます。**")
    st.caption(f"保存ファイル名：{download_name}")
    st.download_button(
        "📥 整理後データをダウンロード",
        data=to_excel_bytes(result.cleaned),
        file_name=download_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )
