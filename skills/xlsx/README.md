# XLSX Skill

来自 Anthropic 官方 Skills 仓库的 Excel 处理 Skill。

原仓库：https://github.com/anthropics/skills/tree/main/skills/xlsx

## 功能

- 📊 读取、编辑、创建 Excel (.xlsx, .xlsm) 文件
- 📈 处理 CSV/TSV 文件
- 🧮 Excel 公式计算和格式化
- 🎨 财务模型颜色编码标准
- ✅ 公式错误检查和重新计算

## 依赖安装

```bash
pip install pandas openpyxl
```

## 依赖工具

- **LibreOffice** - 用于公式重新计算
  ```bash
  # macOS
  brew install libreoffice
  
  # Ubuntu/Debian
  sudo apt-get install libreoffice
  ```

## 文件结构

```
xlsx/
├── SKILL.md                      # Skill 定义（核心）
├── README.md                     # 本文件
├── LICENSE.txt                   # 许可证
└── scripts/
    ├── recalc.py                 # 公式重新计算脚本
    └── office/
        ├── __init__.py
        └── soffice.py            # LibreOffice 辅助工具
```

## 使用示例

### 读取 Excel

```python
import pandas as pd

# 读取数据
df = pd.read_excel('data.xlsx')
print(df.head())
```

### 创建带公式的 Excel

```python
from openpyxl import Workbook
from openpyxl.styles import Font

wb = Workbook()
sheet = wb.active

# 添加数据
sheet['A1'] = 'Revenue'
sheet['A2'] = 1000
sheet['A3'] = 2000

# 添加公式（不是硬编码值！）
sheet['A4'] = '=SUM(A2:A3)'

# 格式化
sheet['A1'].font = Font(bold=True)

wb.save('output.xlsx')

# 重新计算公式
import subprocess
subprocess.run([
    'python', 
    '~/.openclaw/workspace/skills/xlsx/scripts/recalc.py',
    'output.xlsx'
])
```

### 编辑现有文件

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active

# 修改单元格
sheet['B5'] = 'New Value'

# 插入行
sheet.insert_rows(3)

wb.save('modified.xlsx')
```

## 关键规则

### ✅ 使用 Excel 公式，不要硬编码

```python
# ❌ 错误：在 Python 中计算并硬编码
sheet['A10'] = df['Sales'].sum()

# ✅ 正确：使用 Excel 公式
sheet['A10'] = '=SUM(A1:A9)'
```

### 财务模型颜色标准

| 颜色 | 用途 |
|------|------|
| 🔵 蓝色 | 硬编码输入值 |
| ⚫ 黑色 | 公式和计算 |
| 🟢 绿色 | 同工作簿链接 |
| 🔴 红色 | 外部文件链接 |
| 🟡 黄色背景 | 关键假设 |

### 数字格式

- **年份**: "2024" 不是 "2,024"
- **货币**: $#,##0 格式
- **零值**: 显示为 "-"
- **百分比**: 0.0% (一位小数)
- **负数**: (123) 不是 -123

## 公式重新计算

openpyxl 不计算公式值，需要使用 recalc.py：

```bash
python ~/.openclaw/workspace/skills/xlsx/scripts/recalc.py output.xlsx
```

输出示例：
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42
}
```

如有错误：
```json
{
  "status": "errors_found",
  "total_errors": 2,
  "error_summary": {
    "#DIV/0!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

---

*原仓库许可证：Proprietary*
