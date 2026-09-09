# tools/core/model.py

from dataclasses import dataclass

@dataclass
class GlyphRecord:
    """
    glyph_table の 1 レコードを保持するデータ構造。
    b / v は U+XXXX 形式に正規化済みの最終出力用文字列。
    comment は sanitize 済みで、改行・制御コードはスペースに置換済み。
    """
    name: str
    b: str
    v: str
    active: bool
    comment: str
