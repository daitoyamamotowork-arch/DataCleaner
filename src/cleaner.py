"""DataFrame の整理処理。"""

from dataclasses import dataclass, field

import pandas as pd

from .validators import is_valid_url, normalize_phone


@dataclass
class CleaningOptions:
    trim_whitespace: bool = True
    remove_duplicates: bool = True
    detect_blanks: bool = True
    check_urls: bool = True
    normalize_phones: bool = True
    url_columns: list[object] = field(default_factory=list)
    phone_columns: list[object] = field(default_factory=list)


@dataclass
class CleaningResult:
    cleaned: pd.DataFrame
    issues: pd.DataFrame
    original_count: int
    duplicate_count: int
    blank_count: int
    url_error_count: int


def _is_blank(value: object) -> bool:
    return pd.isna(value) or (isinstance(value, str) and not value.strip())


def clean_dataframe(dataframe: pd.DataFrame, options: CleaningOptions) -> CleaningResult:
    """選択された処理を実行し、整理後データと要確認一覧を返す。"""
    cleaned = dataframe.copy()
    issues: list[dict[str, object]] = []

    if options.trim_whitespace:
        # map で文字列だけを対象にし、数値や日付の型は保つ。
        cleaned = cleaned.map(lambda value: value.strip() if isinstance(value, str) else value)

    if options.normalize_phones:
        for column in options.phone_columns:
            if column in cleaned.columns:
                cleaned[column] = cleaned[column].map(normalize_phone)

    duplicate_mask = cleaned.duplicated(keep="first") if options.remove_duplicates else pd.Series(False, index=cleaned.index)
    duplicate_count = int(duplicate_mask.sum())
    if options.remove_duplicates:
        cleaned = cleaned.loc[~duplicate_mask].copy()

    blank_count = 0
    if options.detect_blanks:
        for index, row in cleaned.iterrows():
            for column, value in row.items():
                if _is_blank(value):
                    blank_count += 1
                    issues.append(
                        {
                            "行番号": index + 2,
                            "列名": column,
                            "問題の種類": "空欄",
                            "元の値": dataframe.at[index, column],
                        }
                    )

    url_error_count = 0
    if options.check_urls:
        for column in options.url_columns:
            if column not in cleaned.columns:
                continue
            for index, value in cleaned[column].items():
                # 空欄は空欄チェックに任せ、URLエラーと二重計上しない。
                if not _is_blank(value) and not is_valid_url(value):
                    url_error_count += 1
                    issues.append(
                        {
                            "行番号": index + 2,
                            "列名": column,
                            "問題の種類": "URL要確認",
                            "元の値": dataframe.at[index, column],
                        }
                    )

    issue_columns = ["行番号", "列名", "問題の種類", "元の値"]
    return CleaningResult(
        cleaned=cleaned.reset_index(drop=True),
        issues=pd.DataFrame(issues, columns=issue_columns),
        original_count=len(dataframe),
        duplicate_count=duplicate_count,
        blank_count=blank_count,
        url_error_count=url_error_count,
    )
