import os, json, requests
from bs4 import BeautifulSoup

url = os.environ['DOC_URL']

headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'lxml')

# ===== 调试输出 =====
print("=== 页面标题:", soup.title.string if soup.title else "无标题")
print("=== 页面中所有的 table 数量:", len(soup.find_all('table')))

# 输出前3个 table 的预览内容
for idx, table in enumerate(soup.find_all('table')):
    if idx >= 3:
        break
    rows = table.find_all('tr')
    print(f"\n--- 表格 {idx+1} (行数: {len(rows)}) ---")
    for i, row in enumerate(rows[:4]):  # 只输出前4行
        cells = row.find_all(['th','td'])
        text = [cell.get_text(strip=True) for cell in cells]
        print(f"  行{i}: {text}")
# ===== 调试结束 =====

# 开始解析所有表格
tables = soup.find_all('table')

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

# 你的 Sheet 顺序（请确认与文档底部标签顺序一致）
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

# 保存
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(sheets, f, ensure_ascii=False, indent=2)

print("\n=== 解析完成，各 Sheet 数据量 ===")
for name, data in sheets.items():
    print(f"  {name}: {len(data)} 条")
