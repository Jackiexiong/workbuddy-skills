# 简历格式解析指南

本文档详细说明各格式简历的解析方法、注意事项和常见问题处理方案。

---

## 支持格式总览

| 格式 | 解析难度 | 推荐方案 | 备选方案 |
|------|----------|----------|----------|
| .docx | ★☆☆ | python-docx | pandoc |
| .pdf（文字型） | ★★☆ | pypdf | pdfplumber |
| .pdf（扫描型） | ★★★ | 需要 OCR | 提示用户手动处理 |
| .html | ★★☆ | BeautifulSoup | 自定义 HTML 解析 |
| .txt | ★☆☆ | 直接读取 | — |

---

## 一、Word 文件（.docx）

### 推荐方案：python-docx

```bash
pip install python-docx
```

```python
from docx import Document

def extract_docx(filepath):
    """提取 docx 文件文本内容"""
    doc = Document(filepath)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:  # 跳过空段落
            paragraphs.append(text)
    return '\n'.join(paragraphs)
```

### 备选方案：pandoc

```bash
# 安装 pandoc：https://pandoc.org/installing.html
pandoc "简历.docx" -t plain --wrap=none -o "简历.txt"
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 提取内容缺失表格数据 | python-docx 默认只提取段落 | 增加表格提取 `for table in doc.tables:` |
| 提取到乱码 | 编码问题 | 确保文件不是加密或损坏的 |
| 文件打不开 | .docx 实为 .doc（旧格式） | 提示用户另存为 .docx 格式 |
| 段落顺序错乱 | 文本框/图文框中的内容 | 这是 python-docx 的已知限制，尽量保证关键信息完整 |

#### 提取表格内容增强

```python
def extract_docx_with_tables(filepath):
    """提取 docx 文件文本和表格内容"""
    doc = Document(filepath)
    parts = []
    
    # 提取段落
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            parts.append(text)
    
    # 提取表格
    for i, table in enumerate(doc.tables):
        parts.append(f"\n--- 表格 {i+1} ---")
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            parts.append(' | '.join(cells))
    
    return '\n'.join(parts)
```

---

## 二、PDF 文件

### 方案 A：pypdf（推荐，轻量快速）

```bash
pip install pypdf
```

```python
from pypdf import PdfReader

def extract_pdf(filepath):
    """提取 PDF 文件文本内容"""
    reader = PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text.strip())
    return '\n'.join(pages)
```

### 方案 B：pdfplumber（表格和排版更优）

```bash
pip install pdfplumber
```

```python
import pdfplumber

def extract_pdf_plumber(filepath):
    """使用 pdfplumber 提取 PDF 文本（表格更好）"""
    with pdfplumber.open(filepath) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
            
            # 额外提取表格
            tables = page.extract_tables()
            for table in tables:
                if table:
                    pages.append("\n[表格]")
                    for row in table:
                        pages.append(' | '.join([str(cell or '') for cell in row]))
        return '\n'.join(pages)
```

### 方案 C：检测是否为扫描型 PDF

```python
def is_scanned_pdf(filepath):
    """检测 PDF 是否为扫描件（图片型）"""
    reader = PdfReader(filepath)
    total_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            total_text += text
    
    # 如果提取的文字少于 50 个字符，可能是扫描件
    return len(total_text.strip()) < 50
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 提取为空 | 扫描型 PDF（图片） | 方案 A：`pip install pytesseract` 做 OCR |
| 文字粘连在一起 | PDF 编码问题 | 尝试 pdfplumber 替代 pypdf |
| 提取顺序错乱 | PDF 多列排版 | pdfplumber 对多列支持更好 |
| 中文提取不全 | 字体嵌入问题 | 确保 PDF 字体已嵌入 |
| 表格数据丢失 | 表格在 PDF 中是图形 | pdfplumber 可提取部分表格 |

#### OCR 方案（扫描型 PDF 备用）

如遇到扫描型 PDF，不建议 AI 自动处理（OCR 环境配置复杂），建议提示用户：

> "这份简历是扫描件（图片格式），无法直接提取文字。你可以：
> 1. 使用 Adobe Acrobat 的「导出 PDF」功能导出为 Word
> 2. 使用在线的 PDF 转文字工具
> 3. 重新上传文字版的简历"

如用户坚持使用 OCR，可尝试：

```bash
pip install pytesseract pdf2image
```

---

## 三、HTML 文件

HTML 简历通常来自招聘网站（如 BOSS 直聘、猎聘、智联等）的简历导出功能，结构各异。

### 方案 A：BeautifulSoup（推荐）

```bash
pip install beautifulsoup4
```

```python
from bs4 import BeautifulSoup

def extract_html(filepath):
    """提取 HTML 文件中的可见文本"""
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # 移除 script 和 style 标签
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # 获取文本，用换行分隔
    text = soup.get_text(separator='\n')
    
    # 清理多余空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)
```

### 方案 B：处理不同招聘网站的 HTML 结构

```python
def extract_html_enhanced(filepath):
    """增强 HTML 提取，识别常见简历结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 尝试按常见标签提取结构化信息
    result = []
    
    # 1. 提取标题（候选人姓名通常在 h1/h2 或 title 中）
    title = soup.find('title')
    if title:
        result.append(f"# {title.get_text(strip=True)}")
    
    # 2. 提取所有可见文本
    for tag in soup(['script', 'style', 'meta', 'link']):
        tag.decompose()
    
    text = soup.get_text(separator='\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result.extend(lines)
    
    return '\n'.join(result)
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 提取结果太多噪音 | HTML 中包含导航、广告等 | 使用 `soup.find('body')` 或 `soup.find('main')` 缩小范围 |
| 编码错误 | 网页编码非 UTF-8 | 用 `chardet` 检测编码：`pip install chardet` |
| JavaScript 渲染内容 | 简历内容由 JS 动态生成 | 提示用户使用浏览器「另存为」功能保存完整页面 |
| CSS 类名混淆 | 压缩后的 HTML 类名无意义 | 仍可通过 tag name 提取（div/p/span 等） |

#### 编码检测

```python
import chardet

def detect_and_read(filepath):
    """自动检测编码并读取文件"""
    with open(filepath, 'rb') as f:
        raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding']
    
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()
```

---

## 四、纯文本文件（.txt）

```python
def extract_txt(filepath):
    """直接读取文本文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
```

---

## 五、批量处理脚本模板

将所有格式的解析函数整合为一个统一的接口：

```python
import os

def extract_resume(filepath):
    """统一接口：根据文件扩展名自动选择解析方法"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.docx':
        return extract_docx(filepath)
    elif ext == '.pdf':
        text = extract_pdf(filepath)
        if len(text.strip()) < 50:
            return "[扫描型PDF，无法提取文字]"
        return text
    elif ext == '.html':
        return extract_html(filepath)
    elif ext == '.txt':
        return extract_txt(filepath)
    else:
        return f"[不支持的文件格式: {ext}]"
```

---

## 六、环境准备

首次使用本技能时，可一键准备解析环境：

```bash
pip install python-docx pypdf pdfplumber beautifulsoup4 chardet
```

如遇安装失败，逐条安装即可。

---

## 七、文件命名规范建议

从招聘网站下载的简历文件名通常有规律，可作为候选人姓名提取的辅助：

| 来源 | 常见命名模式 | 说明 |
|------|-------------|------|
| BOSS 直聘 | `张三_Java_5年_简历.pdf` | 含姓名和职位 |
| 猎聘 | `li si_简历.html` | 可能含拼音 |
| 智联 | `resume_12345.html` | 纯数字 ID，需从内容提取姓名 |
| 前程无忧 | `张三+Java开发工程师.pdf` | 含姓名和职位 |
