---
name: resume-screening
description: >
  批量简历筛选技能。从指定文件夹批量解析和筛选简历（支持 .docx / .pdf / .html 格式），
  对照岗位 JD 进行智能匹配和评分，输出排名列表并将最优候选人简历集中到新文件夹。
  用户使用场景：HR 从招聘网站打包下载了大量简历，需要快速筛选出最匹配某岗位的候选人。
  触发词：筛简历、筛选简历、简历筛选、招聘筛选、候选人筛选、帮我挑简历、简历排名、JD 匹配。
version: 1.0.0
compatibility: "需要 Python 环境用于格式解析；pandoc 可选（增强 html/docx 转换）"
---

# 简历筛选技能

批量解析简历文件，对照岗位描述（JD）进行智能匹配和评分，挑选出最合适的 N 份简历并集中存放。

## 工作流程概览

```
用户提供：简历文件夹路径 + 岗位 JD 文本 + 期望选出份数（如 10 份）
    │
    ▼
第 1 步：扫描简历文件夹，列出所有候选文件
第 2 步：批量解析简历内容（支持 .docx / .pdf / .html）
第 3 步：逐份对照 JD 评分
第 4 步：排序并选出 Top N
第 5 步：将选定简历复制到新文件夹
第 6 步：输出排名报告（对话中展示，可选导出 Excel）
```

## 输入

1. **简历文件夹路径**（必填）—— 存放所有简历的目录，支持嵌套子目录
2. **岗位 JD**（必填）—— 招聘职位的原始要求文本（可直接粘贴 JD 全文）
3. **期望选出份数**（可选，默认 10）—— 最终筛选出多少份最合适的简历
4. **额外筛选条件**（可选）—— 如"优先考虑有互联网大厂经验的""排除 985/211 限制"

## 输出

- 在对话中展示排名表（含候选人姓名、匹配分数、关键匹配/不匹配项）
- 将选中的简历文件复制到 `{简历文件夹路径}/_筛选结果_Top{份数}/` 目录
- 可选：导出排名详表为 Excel 文件

## 流程

### 第 1 步：扫描简历文件夹

遍历用户指定的简历文件夹，识别所有候选文件：

```
支持的格式：
  - .docx   — Word 文档（最常用）
  - .pdf    — PDF 文档
  - .html   — 招聘网站导出的 HTML 简历文件
  - .txt    — 纯文本简历

自动忽略：_筛选结果_* 目录、隐藏文件、临时文件（~$ 开头等）
```

使用 `{baseDir}/scripts/export_ranking.py` 辅助扫描：

```bash
python "{baseDir}/scripts/export_ranking.py" --scan "简历文件夹路径"
```

此命令会列出目录结构统计（文件数、格式分布），便于确认扫描范围。

### 第 2 步：批量解析简历内容

对每份简历，根据扩展名使用相应方式提取纯文本内容。

#### 2.1 Word 文件（.docx）

**方案 A（推荐）：python-docx**

```bash
pip install python-docx
python -c "
from docx import Document
doc = Document('路径/简历.docx')
print('\n'.join([p.text for p in doc.paragraphs]))
"
```

**方案 B：pandoc**（处理复杂格式更稳定）

```bash
pandoc "路径/简历.docx" -t plain --wrap=none
```

#### 2.2 PDF 文件（.pdf）

**方案 A（推荐）：pypdf**

```bash
pip install pypdf
python -c "
from pypdf import PdfReader
reader = PdfReader('路径/简历.pdf')
for page in reader.pages:
    print(page.extract_text())
"
```

**方案 B：pdfplumber**（表格和排版更准确）

```bash
pip install pdfplumber
python -c "
import pdfplumber
with pdfplumber.open('路径/简历.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            print(text)
"
```

#### 2.3 HTML 文件（.html）

直接读取 HTML 后提取可见文本：

```bash
python -c "
from html.parser import HTMLParser
import re

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            stripped = data.strip()
            if stripped:
                self.text.append(stripped)

with open('路径/简历.html', 'r', encoding='utf-8') as f:
    content = f.read()
extractor = TextExtractor()
extractor.feed(content)
text = '\n'.join(extractor.text)
print(text)
"
```

或使用 BeautifulSoup：

```bash
pip install beautifulsoup4
python -c "
from bs4 import BeautifulSoup
with open('路径/简历.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
print(soup.get_text(separator='\n'))
"
```

> **批处理技巧**：对所有简历文件，可以用一个循环统一处理。你可以让 AI 助手（也就是我）逐份读取并解析，不需要用户手动逐份操作。

### 第 3 步：逐份对照 JD 评分

对每份简历，对照岗位 JD，从以下 **6 个维度** 进行评分（满分 100 分制）：

| 维度 | 权重 | 说明 |
|------|------|------|
| **硬性条件匹配** | 30% | 学历、专业、工作年限、证书等硬门槛 |
| **技能栈匹配** | 25% | JD 中列出的技术栈、工具、语言等掌握程度 |
| **项目/经验匹配** | 20% | 过往项目经验与岗位职责的吻合度 |
| **软性素质** | 10% | 沟通能力、团队协作、管理经验等 |
| **行业/公司背景** | 10% | 相关行业经验、知名公司经历 |
| **简历质量** | 5% | 简历结构清晰度、信息完整度、表达专业度 |

**评分原则：**

- **硬性条件不满足则直接淘汰**（如一页否决项：学历要求硕士以下但候选人为大专），标记为"不匹配"并说明原因，不再继续评分
- 其余维度给出 1-10 分的细化评分，按权重加权得总分
- 每份简历必须给出 **匹配摘要**（3-5 句话说明为什么匹配/不匹配）
- 标注 **关键匹配项**（绿色）和 **关键差距项**（红色）

#### 评分参考标准

详细评分标准参考 `references/screening-criteria.md`。

### 第 4 步：排序并选出 Top N

1. 将所有评分完成的简历按总分降序排列
2. 取前 N 份（用户指定的份数，默认 10）
3. 如果第 N 名有并列，将所有并列者纳入候选池
4. 如果硬性条件达标者不足 N 份，如实提示用户

### 第 5 步：将选定简历复制到新文件夹

创建目标目录 `{简历文件夹路径}/_筛选结果_Top{份数}/`，将选中的简历文件复制进去：

```bash
python "{baseDir}/scripts/export_ranking.py" \
  --copy "简历文件夹路径" \
  --top 10 \
  --files "简历1.docx" "简历2.pdf" "简历3.html"
```

或者使用操作系统命令：

```bash
mkdir -p "简历文件夹路径/_筛选结果_Top10"
cp "简历文件夹路径/张三_简历.docx" "简历文件夹路径/_筛选结果_Top10/"
```

### 第 6 步：输出排名报告

在对话中展示完整的排名报告，格式如下：

```
╔══════════════════════════════════════════════════════════╗
║             简历筛选结果报告                            ║
║             岗位：高级 Python 后端工程师                 ║
║             简历总量：47 份  |  筛选 Top：10 份         ║
╚══════════════════════════════════════════════════════════╝

📊 排名总览
────────────────────────────────────────────────────────
  # │ 候选人    │ 总分 │ 硬性条件 │ 关键匹配
━━━━┿━━━━━━━━━━┿━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━
  1 │ 张三      │ 92   │ ✅ 通过  │ Python/Django/5年经验
  2 │ 李四      │ 87   │ ✅ 通过  │ Go/分布式/高并发
  3 │ 王五      │ 85   │ ✅ 通过  │ Python/Flask/3年经验
  ⋮
 10 │ 赵六      │ 71   │ ✅ 通过  │ Java转Python/学习能力强
────────────────────────────────────────────────────────

📋 每份简历详情
────────────────────────────────────────────────────────

【第 1 名】张三 — 92 分
  ✅ 硬性条件：硕士 / 计算机专业 / 5年经验
  ✅ 技能栈：Python(精通) Django(精通) Redis(熟练) Docker(熟练)
  ✅ 项目：电商平台架构设计，日活 100w+
  ⚠️ 差距：无管理经验
  匹配摘要：候选人技术栈与岗位高度吻合，有大型项目经验，推荐面试。

【第 2 名】李四 — 87 分
  ✅ 硬性条件：本科 / 软件工程 / 6年经验
  ✅ 技能栈：Go(精通) 分布式系统(精通) Python(熟练)
  ⚠️ 差距：Python 经验相对较少，可能需要短期适应
  匹配摘要：候选人后端功底扎实，虽主语言为 Go 但 Python 能力可迁移，推荐面试。
  ⋮

📁 已保存文件
────────────────────────────────────────────────────────
  选定简历已复制到：简历文件夹/_筛选结果_Top10/
  
💡 建议下一步
────────────────────────────────────────────────────────
  • 建议对 Top 10 候选人安排技术一面
  • 第 8-10 名候选人可考虑作为备选
  • 对于硬性条件不达标但技能突出的候选人（如 xxx），可考虑破格
```

同时生成排名 CSV 文件（可选）：

```bash
python "{baseDir}/scripts/export_ranking.py" \
  --export "简历文件夹路径/_筛选结果_Top10/排名表.csv"
```

## 示例

### 示例 1：标准筛选流程

**用户说：** "帮我筛选一下 D:\简历库\Java后端 这个文件夹里的简历，JD 是：本科以上，3 年以上 Java 开发经验，熟悉 Spring Boot、微服务架构，有电商经验优先。挑出最合适的 10 份。"

**你的操作：**

1. 扫描文件夹，确认文件数量和格式
2. 逐份解析简历内容
3. 对照 JD 逐项评分
4. 排序取 Top 10
5. 复制到 `_筛选结果_Top10/` 目录
6. 输出完整排名报告

### 示例 2：追加筛选条件

**用户说：** "在上次筛选结果的基础上，只要 985/211 毕业的。"

**你的操作：**

1. 确认是针对已选出的 Top 10 还是原始简历库
2. 如果是原始简历库，在评分中增加"学历背景"硬性过滤
3. 生成新的排名和筛选结果

### 示例 3：量大多批次处理

**用户说：** "这里有 200 多份简历，先帮我粗筛一遍，淘汰明显不合适的，剩下的再精细评分。"

**你的操作：**

1. 第一轮：快速扫描，硬性条件不达标 → 直接淘汰
2. 第二轮：对剩余简历进行 6 维度精细评分
3. 汇总输出

## 参考文件

- `references/screening-criteria.md` — 各维度详细评分标准与打分指南
- `references/format-support.md` — 各简历格式的解析方法和常见问题处理
- `scripts/export_ranking.py` — 排名导出和文件操作辅助工具

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| PDF 提取为空 | 扫描型 PDF（图片），非文字 PDF | 使用 OCR 方案：`pypdf` 不支持 → 提示用户用 Adobe 导出文字 |
| HTML 排版混乱 | 不同招聘网站 HTML 结构差异大 | 用 BeautifulSoup 统一提取可见文本，忽略样式和脚本 |
| docx 无法解析 | 文件损坏或加密 | 尝试用 pandoc 作为备选方案 |
| 编码乱码 | 文件编码不是 UTF-8 | 尝试 `chardet` 检测编码后再读取 |
| 简历非常多（200+） | 逐份处理耗时较长 | 先用批量硬性过滤（关键词匹配）缩小范围，再精细评分 |
| 简历文件名没有候选人姓名 | 从招聘网站下载的默认文件名 | 解析简历内容中的姓名字段，输出时使用解析到的姓名 |

### 关键命令速查

```bash
# 扫描简历文件夹
python "{baseDir}/scripts/export_ranking.py" --scan "简历文件夹路径"

# 批量导出排名
python "{baseDir}/scripts/export_ranking.py" \
  --rankings "候选人1:92,候选人2:87,..." \
  --export "输出路径/排名表.csv" \
  --title "岗位名称"

# 复制选中简历
python "{baseDir}/scripts/export_ranking.py" \
  --copy "源文件夹" --top 10 \
  --files "简历1.docx" "简历2.pdf"
```
