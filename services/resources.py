from bs4 import BeautifulSoup
import requests
import sqlite3
from services.database import DB_PATH

print(f"数据库文件路径: {DB_PATH}")

# 模拟请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_video_numbers_for_actor(actor_name):
    """
    根据演员名称爬取番号和资源。
    """
    websites = [
        ("av-wiki.net", f"https://www.av-wiki.net/?s={actor_name}&post_type=product"),
        ("javbus", f"https://www.javbus.com/search/{actor_name}")
    ]
    video_numbers = []

    for website, url in websites:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"爬取 {website} 失败: HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            if website == "av-wiki.net":
                video_numbers += [item.text.strip() for item in soup.find_all("li") if item.text.strip()]
            elif website == "javbus":
                video_numbers += [item.text.strip() for item in soup.find_all("div", class_="item-tag")]

        except Exception as e:
            print(f"爬取 {website} 失败: {e}")
            continue

    # 去重并返回结果
    return list(set(video_numbers))

def store_resources(actor_id, video_numbers):
    """
    存储爬取的资源到数据库。
    :param actor_id: 演员的 ID
    :param video_numbers: 爬取的番号列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for video_number in video_numbers:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO resources (actor_id, title, magnet)
                VALUES (?, ?, ?)
            """, (actor_id, video_number, "magnet_placeholder"))
        except Exception as e:
            print(f"存储资源 {video_number} 失败: {e}")
            continue

    conn.commit()
    conn.close()

def get_all_actors():
    """
    从数据库中获取所有演员。
    :return: 演员列表（包含 ID 和名称）
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM actors")
    actors = cursor.fetchall()

    conn.close()
    return actors

def crawl_and_store_resources():
    """
    主函数：从数据库中提取演员，爬取番号，并存储到数据库。
    """
    # 获取所有演员
    actors = get_all_actors()
    if not actors:
        print("没有找到需要爬取的演员。")
        return

    print(f"共找到 {len(actors)} 位演员，开始爬取资源...")

    for actor_id, actor_name in actors:
        print(f"正在爬取演员：{actor_name}")

        # 爬取资源
        video_numbers = fetch_video_numbers_for_actor(actor_name)
        if not video_numbers:
            print(f"未找到演员 {actor_name} 的任何资源。")
            continue

        # 存储资源到数据库
        store_resources(actor_id, video_numbers)
        print(f"成功存储演员 {actor_name} 的资源，共 {len(video_numbers)} 条记录。")

    print("所有资源爬取完成！")
