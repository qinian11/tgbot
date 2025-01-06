import requests
from bs4 import BeautifulSoup

# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
    'Cache-Control': 'max-age=0',
    'Cookie': 'PHPSESSID=uane8of7trofk167sqiqhht070; existmag=all; 4fJN_2132_saltkey=yck0CwX1; 4fJN_2132_lastvisit=1735992619; 4fJN_2132_seccodecSTREqDr=50755.2a8ee4b55db2a1b8d0; age=verified; dv=1; 4fJN_2132_sid=GSSz2u; 4fJN_2132_seccodecSAeI9GSSz2u=31543.167703665dd0323581; 4fJN_2132_seccodecSAPNCGSSz2u=31637.96a7af5576d1d0fe3c; 4fJN_2132_seccodecSGSSz2u=32007.dce709d8547ac8533f; 4fJN_2132_lastact=1736068363%09member.php%09register',
    'Referer': 'https://www.javbus.com/',
    'Sec-CH-UA': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

# 基本的URL
base_url = 'https://www.javbus.com'

# 存储所有演员的名字
all_actors = []

# 初始页面
current_url = base_url + '/actresses'

while True:
    print(f"正在爬取页面: {current_url}")

    # 发起请求并获取页面内容
    response = requests.get(current_url, headers=headers)
    response.encoding = 'utf-8'

    # 检查页面是否成功返回
    if response.status_code != 200:
        print(f"无法访问页面: {current_url}，状态码：{response.status_code}")
        break  # 如果该页无法访问，终止爬取

    # 使用BeautifulSoup解析页面
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有演员名字（假设在 <span> 标签内）
    actors = soup.select('div.photo-info span')  # CSS选择器获取所有演员名字
    actor_names = [actor.text.strip() for actor in actors if actor.text.strip()]

    # 如果该页没有演员名字，说明爬取完成
    if not actor_names:
        print(f"页面 {current_url} 没有演员数据，停止爬取")
        break

    # 打印该页爬取到的演员名字
    print(f"页面 {current_url} 爬取了 {len(actor_names)} 个演员")

    # 将该页的演员名字添加到总列表中
    all_actors.extend(actor_names)

    # 查找“下一页”按钮
    next_page = soup.select_one('a#next')  # 通过 id="next" 来查找
    if not next_page:
        print(f"没有找到下一页，停止爬取")
        break

    # 如果找到了“下一页”链接，则更新 current_url
    next_href = next_page['href']  # 获取 href 属性
    current_url = base_url + next_href

# 导出所有演员名字到 text 文件，每个名字用换行符分隔
with open('actors.txt', 'w', encoding='utf-8') as f:
    f.write(' '.join(all_actors))

print(f"成功爬取并保存了 {len(all_actors)} 个演员名字到 actors.txt")
