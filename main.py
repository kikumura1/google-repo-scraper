import time
import sqlite3
import requests
from bs4 import BeautifulSoup

# 1. GoogleのGitHubリポジトリ一覧を取得（スクレイピング）
# ※要件: APIは使わずにスクレイピングする
url = "https://github.com/orgs/google/repositories"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("スクレイピングを開始します...")
response = requests.get(url, headers=headers)

# ※要件: time.sleep(1) を入れる
time.sleep(1)

soup = BeautifulSoup(response.text, "html.parser")

# リポジトリ情報の抽出
data_list = []

# Googleの組織ページ上のリポジトリ要素を取得
# (GitHubの構造に対応するため、複数のセレクタでフォールバック設定)
repo_elements = soup.select("article") or soup.select("li.Box-row") or soup.select("div[data-filterable-for]")

for repo in repo_elements:
    # リポジトリ名
    name_tag = repo.select_one("a[aria-describedby]") or repo.select_one("h3 a") or repo.select_one("a")
    repo_name = name_tag.text.strip() if name_tag else "N/A"
    
    # 主要言語
    lang_tag = repo.select_one("[itemprop='programmingLanguage']") or repo.select_one("span[class*='language']")
    language = lang_tag.text.strip() if lang_tag else "Unknown"
    
    # スター数
    star_tag = repo.select_one("a[href*='/stargazers']") or repo.select_one("a[href*='/stargazers'] svg")
    if star_tag:
        stars = star_tag.parent.text.strip() if star_tag.parent else star_tag.text.strip()
    else:
        stars = "0"
        
    data_list.append((repo_name, language, stars))

print(f"{len(data_list)} 件のデータを取得しました。")

# 2. データベース（SQLite）の作成とデータ保存
conn = sqlite3.connect("google_repos.db")
cursor = conn.cursor()

# テーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT,
    language TEXT,
    stars TEXT
)
""")

# スクレイピングしたデータをDBへ保存
cursor.executemany("""
INSERT INTO repositories (repo_name, language, stars)
VALUES (?, ?, ?)
""", data_list)

conn.commit()
print("データをデータベースに保存しました。")

# 3. 保存したデータをSELECT文で表示（課題要件）
print("\n--- データベースの内容 (SELECT * FROM repositories) ---")
cursor.execute("SELECT * FROM repositories")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]} | リポジトリ名: {row[1]} | 言語: {row[2]} | スター数: {row[3]}")

conn.close()