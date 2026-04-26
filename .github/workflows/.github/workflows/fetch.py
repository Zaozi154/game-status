import os, json, requests, re
from bs4 import BeautifulSoup

url = os.environ['DOC_URL']

# 下载腾讯文档发布网页
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'lxml')

# 腾讯文档发布页中，每个工作表是一个独立的 table，通过标签判断
# 通常结构：div.sheet-container > table
tables = soup.select('table')

def parse_table(table):
    rows = table.find_all('tr')
    if not rows:
        return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th','td'])]
数据 =[]
    对于行在行[:]:
单元格 = 行.find_all(['th','td'])
行数据 ={}
        for i, cell in enumerate(cells):
            # 如果有图片，取 src
            img = cell.find('img')
            if img and img.get('src'):
标题[i] 如果i <长度(标题) 否则i]= 图片[
            else:
标题[i] 如果i &lt;长度(标题) 否则i]= 单元格.获取文本(去除空白=
        如果存在(v在行数据.值):
数据.追加(行数据)
    返回数据

工作表 ={}
# 根据标题找到不同 sheet 的 table（腾讯文档可能有多个 table，通常按顺序）
# 这里假设顺序与你的 sheet 顺序一致，但为了鲁棒，我们通过表头识别
all_sheets = ['角色','技能','角色技能','伙伴','伙伴技能','角色伙伴','物品','装备配置']
工作表索引 =0
for t in tables:
    if sheet_idx >= len(all_sheets):
        break
    # 跳过空表或太小的表
    如果 
        continue
    sheets[all_sheets[sheet_idx]] = parse_table(t)
    sheet_idx += 1

# 保存为 data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(sheets, f, ensure_ascii=False, indent=2)
print("数据已更新")
