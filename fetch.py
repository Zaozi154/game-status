import os, json, requests

url = os.environ['DOC_URL']

headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=30)

# ===== 输出响应状态和内容前 2500 字符 =====
print("=== 状态码:", resp.status_code)
print("=== 响应头 Content-Type:", resp.headers.get('Content-Type', ''))
print("=== 页面文本前 2500 字符 ===")
print(resp.text[:2500])
# ===== 诊断结束 =====

# 如果状态码不是200，直接退出
if resp.status_code != 200:
    print("\n❌ 请求失败，请检查 DOC_URL 是否有效，或是否需要登录。")
    exit(1)

# 尝试解析
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, 'lxml')
tables = soup.find_all('table')
print(f"\n=== 找到的 table 数量: {len(tables)}")
if len(tables) == 0:
    print("⚠️ 没有找到任何表格，页面可能是动态加载的。")
    # 可以再检查是否有 iframe
    iframes = soup.find_all('iframe')
    print(f"页面中 iframe 数量: {len(iframes)}")
    for iframe in iframes:
        print("  iframe src:", iframe.get('src'))
    exit(1)

def parse_table(table):
    rows = table.find_all('tr')
    if not rows:
        return []
    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th','td'])]
    data = []
    for row in rows[1:]:
        cells = row.find_all(['th','td'])
        row_data = {}
        for i, cell in enumerate(cells):
            img = cell.find('img')
            if img and img.get('src'):
                row_data[headers[i] if i < len(headers) else i] = img['src']
            else:
                row_data[headers[i] if i < len(headers) else i] = cell.get_text(strip=True)
        if any(v for v in row_data.values()):
            data.append(row_data)
    return data

all_sheets = ['角色','技能','角色技能','伙伴','伙伴技能','角色伙伴','物品','装备配置']
sheets = {}
sheet_idx = 0
for t in tables:
    if sheet_idx >= len(all_sheets):
        break
    if len(t.find_all('tr')) < 2:
        continue
    sheets[all_sheets[sheet_idx]] = parse_table(t)
    sheet_idx += 1

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(sheets, f, ensure_ascii=False, indent=2)

print("\n=== 解析完成，各 Sheet 数据量 ===")
for name, data in sheets.items():
    print(f"  {name}: {len(data)} 条")
