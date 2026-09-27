# tools/core/normalize.py

def to_uplus_string(s: str) -> str:
    """
    例外を出さず、次の手順で変換する:
        1. "_" で分割
        2. 前後のスペースを除去
        3. U+ で始まらなければ U+ を付与
        4. 大文字化
    """

    if not s:
        return ""

    s = s.strip()

    # "_" があれば分割、なければ単体として扱う
    parts = s.split("_")

    out = []
    for part in parts:
        part = part.strip()

        # U+ が付いていなければ付与
        if not part.startswith("U+"):
            part = "U+" + part

        # 大文字化
        part = part.upper()

        out.append(part)

    return " ".join(out)


def validate_uplus_input(s: str) -> tuple[bool, str]:
    """
    許可する形式:
        - "U+3404"
        - "U+3404 U+E0101"

    True/False と理由を返す。
    """

    if not s:
        return False, "Empty string"

    parts = s.split()

    for part in parts:
        if not part.startswith("U+"):
            return False, f"Invalid format (must start with U+): {part}"

        hex_part = part[2:]
        try:
            int(hex_part, 16)
        except ValueError:
            return False, f"Invalid hex code: {hex_part}"

    return True, ""


def pick_ucs_by_rep(ucs_raw: str, rep: str) -> str:
    """
    UCS の候補文字列 ucs_raw を ';' で分割し、
    各要素を to_uplus_string() で正規化したうえで、
    正規化後の文字列が rep で始まるものを優先的に選択する。
    一致するものが無ければ、正規化後の最初の要素を返す。

    例:
        ucs_raw = "2B9E4_E0100;535A_E010A"
        rep     = "U+535A"
        → "U+535A U+E010A" を返す
    """

    rep_norm = rep.strip()

    # 1) ucs_raw を ';' で分割
    parts = [p.strip() for p in ucs_raw.split(";")]

    # 2) 各要素を U+XXXX 形式に正規化
    normalized = [to_uplus_string(p) for p in parts]

    # 3) rep で始まるものを探す
    for norm in normalized:
        if norm.startswith(rep_norm):
            return norm

    # 4) 見つからなければ最初の要素
    return normalized[0]



def sanitize_comment(comment: str) -> str:
    """
    comment の改行や制御コードをスペースに置換し、
    連続スペースを 1 個にまとめて 1 行にする。
    """

    out = []

    for ch in comment:
        code = ord(ch)

        # 改行・制御コード → スペース
        if ch in ("\n", "\r") or code < 0x20 or code == 0x7F:
            out.append(" ")
        else:
            out.append(ch)

    # 連続スペースを 1 個にまとめる
    return " ".join("".join(out).split())
