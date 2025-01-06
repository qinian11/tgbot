import requests
from bs4 import BeautifulSoup
from datetime import datetime, date


def fetch_resources_from_javdb(actor_name, page_number):
    """
    从 Javdb 获取资源。
    :param actor_name: 演员名称
    :param page_number: 当前页数
    :return: 抓取的资源列表
    """
    url = f"https://www.javdb.com/star/{actor_name}?page={page_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"无法访问页面 {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    resources = []

    for item in soup.find_all('div', class_='video-item'):
        title = item.find('h3').text.strip()
        link = item.find('a')['href']
        image_url = item.find('img')['src']
        video_number = title.split(" ")[0]
        release_date_text = item.find('span', class_='date').text.strip()

        try:
            release_date = datetime.strptime(release_date_text, "%Y-%m-%d").date()
        except ValueError:
            release_date = None

        if release_date and release_date >= date.today():
            resources.append({
                'title': title,
                'link': link,
                'image_url': image_url,
                'video_number': video_number,
                'main_actor': actor_name,
                'release_date': release_date
            })

    return resources
