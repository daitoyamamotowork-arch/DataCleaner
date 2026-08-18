# DataCleaner

## ツール概要

DataCleaner は、事務作業や Web リサーチで作成した CSV・Excel データをブラウザ上で確認・整理するシンプルな Web アプリです。処理は画面のチェックボックスで選べます。

## 主な機能

- CSV / Excel（`.xlsx`）のアップロードとプレビュー
- 文字列の前後の空白削除、完全一致する重複行の削除
- 空欄と不正 URL の「要確認」一覧表示（元の値は勝手に修正しません）
- 電話番号の全角数字の半角化、ハイフンの統一、前後の空白削除
- 整理後データの Excel ダウンロード

## 使用技術

- Python
- Streamlit
- pandas
- openpyxl

## インストール方法

Python 3.10 以上を用意し、このリポジトリで次を実行します。仮想環境の利用を推奨します。

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 起動方法

```bash
streamlit run app.py
```

ブラウザで表示された画面に CSV または `.xlsx` をアップロードしてください。`sample_data/sample_dirty.csv` には、重複、空欄、不正 URL、全角の電話番号、前後に空白がある値を収録しています。
