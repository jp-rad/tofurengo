import os
import re
import zipfile
import urllib.request
from pathlib import Path

TARGET_FILES = [
    {
        "file_name": "deluxe文字選択DWPI明朝4.10版V2.0.mdb",
        "type": "gdrive_zip_extract",
        "file_id": "1BrUGWPNn-afklRKVbyGAr2v5zgwOdgdw",
    },
    {
        "file_name": "deluxe文字選択DWPIex明朝1.2版.mdb",
        "type": "gdrive_zip_extract",
        "file_id": "1AVSI9x_vjTBWFKT5C9RnXIs82tpqkdy6",
    },
    {
        "file_name": "mji.00602.xlsx",
        "type": "direct",
        "url": "https://moji.or.jp/wp-content/uploads/2024/01/mji.00602.xlsx",
    },
    {
        "file_name": "MJIH00201.xlsx",
        "type": "zip_extract",
        "url": "https://moji.or.jp/wp-content/mojikiban/oscdl/MJIH00201-xlsx.zip",
    },
]

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def download_url(url: str, save_path: Path):
    """URLからファイルを直接ダウンロード"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(save_path, "wb") as f:
        f.write(response.read())

def download_gdrive(file_id: str, save_path: Path):
    """Google Drive のウイルススキャン警告画面を回避して取得"""
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req) as response:
        content = response.read()
        if content.startswith(b"<!DOCTYPE html") or b"<html" in content[:200]:
            html_text = content.decode("utf-8", errors="ignore")
            match = re.search(r'href="(/download\?[^"]+confirm=[^"]+)"', html_text)
            if match:
                confirm_url = "https://drive.usercontent.google.com" + match.group(1).replace("&amp;", "&")
                req_confirm = urllib.request.Request(confirm_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_confirm) as res_final, open(save_path, "wb") as f:
                    f.write(res_final.read())
                return
        with open(save_path, "wb") as f:
            f.write(content)

def extract_file_from_zip(zip_path: Path, file_name: str, dest_dir: Path):
    """ZIP内の全階層から file_name に完全一致（大文字小文字無視）するファイルを抽出・保存"""
    target_lower = file_name.lower()
    
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            
            # 純粋なファイル名を取得して比較
            name_inside_zip = Path(member.filename).name
            if name_inside_zip.lower() == target_lower:
                target_path = dest_dir / file_name
                with z.open(member) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())
                print(f"[downloader] [OK] Extracted: {file_name} (from {zip_path.name})")
                return

    # ZIP内に見つからない場合はエラーを出力
    with zipfile.ZipFile(zip_path, "r") as z:
        file_list = [m.filename for m in z.infolist()]
    raise FileNotFoundError(f"'{file_name}' not found inside {zip_path.name}. Contents: {file_list}")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for target in TARGET_FILES:
        file_name = target["file_name"]
        t_type = target["type"]

        # すでにファイルが存在する場合は処理をスキップ
        dest_file_path = DATA_DIR / file_name
        if dest_file_path.exists():
            print(f"[downloader] [SKIP] Already exists: {file_name}")
            continue

        if t_type == "direct":
            # 直接ダウンロードしたファイルを一旦展開ファイル名で保存し、zip化
            zip_path = DATA_DIR / f"{file_name}.zip"

            print(f"[downloader] Downloading {file_name}...")
            download_url(target["url"], dest_file_path)
            
            # ZIPアーカイブを作成して格納
            print(f"[downloader] Zipping {file_name} -> {zip_path.name}...")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(dest_file_path, arcname=file_name)
            
            print(f"[downloader] [OK] Saved & Zipped: {file_name} -> {zip_path.name}")

        elif t_type in ("zip_extract", "gdrive_zip_extract"):
            # ZIPとしてダウンロード後、解凍して抽出
            zip_path = DATA_DIR / f"{file_name}.zip"

            print(f"[downloader] Downloading ZIP: {zip_path.name}...")
            if t_type == "zip_extract":
                download_url(target["url"], zip_path)
            else:
                download_gdrive(target["file_id"], zip_path)

            extract_file_from_zip(zip_path, file_name, DATA_DIR)

if __name__ == "__main__":
    main()
