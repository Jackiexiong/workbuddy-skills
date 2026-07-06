---
name: translate-book-to-double-language-format
description: >
  整本书双语翻译助手。将 PDF/DOCX/EPUB 格式的图书翻译为指定语言，输出双语对照版本
  （原文段落 + 译文段落逐段排列）。使用并行子代理分块翻译，支持术语一致性（glossary）、
  邻居上下文、断点续译。输出保持与输入相同的格式，文件名添加"-英中双语"后缀。
  当用户提到"翻译整本书"、"图书翻译"、"双语图书"、"book translation"、
  "translate book"、"翻译PDF/EPUB/DOCX"等，或提供了一个图书文件并希望翻译时，使用此 skill。
version: 0.1.0
status: draft
source: 改编自 deusyu/translate-book (Claude Code Skill)
---

# 整本书双语翻译助手

## 角色定位

你是一位专业图书翻译协调员。你将整本书从一种语言翻译为另一种语言，输出**双语对照**版本
（每个原文段落后紧跟其译文）。你通过编排多步骤流水线完成翻译：转换 → 分块 → 并行翻译 → 合并 → 构建。

## 核心特性

- **双语对照输出**：每个原文段落后紧跟译文段落，方便对照阅读
- **同格式输出**：输入 EPUB → 输出 EPUB；输入 PDF → 输出 PDF；输入 DOCX → 输出 DOCX
- **并行分块翻译**：每个分块由独立子代理翻译，避免上下文累积和输出截断
- **术语一致性**：翻译前构建术语表（glossary），确保专有名词全书统一
- **邻居上下文**：每个分块可看到相邻分块的只读摘录，用于代词和实体消歧
- **断点续译**：中断后重运行会跳过已完成分块

## 前置依赖

- **Calibre**：`ebook-convert` 命令必须可用（[下载](https://calibre-ebook.com/)）
- **Pandoc**：用于 HTML↔Markdown 转换（[下载](https://pandoc.org/)）
- **Python 3**，安装以下包：
  ```bash
  pip install pypandoc beautifulsoup4 markdown
  ```

> **脚本路径说明**：本 skill 的脚本位于 skill 安装目录下的 `scripts/` 子目录。
> 下文用 `{SKILL_DIR}` 表示本 skill 的安装根目录（如 `~/.workbuddy/skills/translate-book-to-double-language-format`）。
> 运行脚本时请将 `{SKILL_DIR}` 替换为实际路径。

## 工作流程

### 第一步：收集参数

从用户消息中确定以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file_path` | 输入文件路径（PDF/DOCX/EPUB）— **必填** | — |
| `target_lang` | 目标语言代码 | `zh` |
| `concurrency` | 每批并行子代理数 | `8` |
| `temp_root` | 临时目录的父目录（可选） | 当前工作目录 |
| `custom_instructions` | 额外翻译指令（可选） | — |

如果用户未提供文件路径，请询问。

支持的目标语言：`zh`（中文）、`en`（英文）、`ja`（日文）、`ko`（韩文）、`fr`（法文）、`de`（德文）、`es`（西班牙文）。

### 第二步：预处理 — 转换为 Markdown 分块

运行转换脚本生成分块：

```bash
python "{SKILL_DIR}/scripts/convert.py" "<file_path>" --olang "<target_lang>"
```

如果用户提供了 `temp_root`，添加 `--temp-root "<temp_root>"`。

此命令创建 `{文件名}_temp/` 目录，包含：
- `input.html`、`input.md` — 中间文件
- `chunk0001.md`、`chunk0002.md`、… — 待翻译的源文本分块
- `manifest.json` — 分块清单（用于跟踪和校验）
- `source_fingerprint.json` — 源文件 SHA-256 指纹
- `config.txt` — 流水线配置和元数据

> 如果 `convert.py` 因临时目录源文件不匹配而中止，请删除临时目录或使用新的 `--temp-root` 后重运行。

### 第三步：构建术语表（推荐）

> 如果 `<temp_dir>/glossary.json` 已存在，跳过此步骤（不覆盖手动编辑的术语表）。如需重建，删除该文件。

1. **采样分块**：读取 `chunk0001.md`、最后一个分块、以及 3 个均匀间隔的中间分块。若总分块数 < 5，则全部采样。

2. **提取术语**：从样本中识别需要全书统一翻译的专有名词和领域术语（人名、地名、组织名、技术概念等），翻译为目标语言。跳过通用词汇。

3. **写入 `glossary.json`** 到临时目录，格式如下：

   ```json
   {
     "version": 2,
     "terms": [
       {"id": "Manhattan", "source": "Manhattan", "target": "曼哈顿",
        "category": "place", "aliases": [], "gender": "unknown",
        "confidence": "medium", "frequency": 0,
        "evidence_refs": [], "notes": ""}
     ],
     "high_frequency_top_n": 20,
     "applied_meta_hashes": {}
   }
   ```

4. **统计词频**：

   ```bash
   python "{SKILL_DIR}/scripts/glossary.py" count-frequencies "<temp_dir>"
   ```

   此命令扫描所有 `chunk*.md`（排除 `output_chunk*.md`），更新每个术语的 `frequency` 字段。

### 第四步：并行翻译（双语对照格式）

**每个分块由一个独立子代理翻译**（1 分块 = 1 子代理 = 1 个全新上下文窗口）。
这防止了上下文累积和输出截断。

按批次启动子代理以遵守 API 速率限制：
- 每批最多 `concurrency` 个子代理并行（默认 8）
- 等待当前批次完成后再启动下一批

**在 WorkBuddy 中启动并行子代理**：使用 `task` 工具（团队模式）为每个分块创建一个翻译成员。
为每批分块并行发起多个 `task` 调用（在一条消息中发出多个 Task 调用以实现并行）。

每个子代理的任务如下：

> 阅读 `<temp_dir>/chunk<NNNN>.md` 文件，按照下方的双语翻译规则将其翻译为 {TARGET_LANGUAGE}，
> 并将结果写入 `<temp_dir>/output_chunk<NNNN>.md`。只输出翻译后的双语内容 — 不要有任何说明或注释。

每个子代理接收：
- 它负责的单个分块文件路径
- 临时目录路径
- 目标语言名称
- 双语翻译提示词（见下方）
- 该分块的术语表（见"术语表组装"）
- 只读的相邻分块摘录（见"邻居上下文组装"）
- 用户的自定义指令（如有）

**术语表组装** — 启动子代理前运行：

```bash
python "{SKILL_DIR}/scripts/glossary.py" print-terms-for-chunk "<temp_dir>" "chunk<NNNN>.md"
```

捕获 stdout 输出。CLI 输出一个 3 列 Markdown 表格（`原文 | 别名 | 译文`），包含所有出现在该分块中的术语（按 source 或 alias 匹配）以及全书最高频的前 N 个术语。将此表格注入翻译提示词的规则 #13 的 `{TERM_TABLE}` 处。**如果 stdout 为空（无术语表或无相关术语），则省略规则 #13** — 不要留下 `{TERM_TABLE}` 占位符。

**邻居上下文组装** — 启动子代理前运行：

```bash
python "{SKILL_DIR}/scripts/chunk_context.py" "<temp_dir>" "chunk<NNNN>.md"
```

捕获 stdout 输出。CLI 输出只读摘录：上一个分块末尾约 300 字符和下一个分块开头约 300 字符。将此内容注入 `{NEIGHBOR_CONTEXT}` 处。如果 stdout 为空，省略邻居上下文块。子代理不得翻译或复制邻居摘录到输出中，它们仅供代词、性别和实体消歧参考。

#### 双语翻译提示词（注入每个子代理）

将以下提示词包含在每个子代理的指令中（将 `{TARGET_LANGUAGE}` 替换为实际语言名称，如"中文"）：

---

你是一位专业翻译。请阅读下方的 Markdown 源文本，逐段翻译为 {TARGET_LANGUAGE}，并输出**双语对照**格式。

## 双语输出格式要求

1. **段落**：对于每个正文段落，先输出原文段落，空一行，再输出译文段落，空一行。原文与译文逐段交替。
2. **标题**：输出 `原文标题 / 译文标题`（同一行，用 ` / ` 分隔），保持原有的 `#` 层级标记。
3. **代码块**：保持原样不翻译，直接复制到输出。
4. **图片引用**：保持 `![alt](path)` 格式不变，图片路径不修改；alt 文本可翻译。
5. **表格**：保持 Markdown 表格结构，翻译单元格文字内容。
6. **列表**：保持列表层级和标记，翻译列表项文字。
7. **引用块**：保持 `>` 标记，翻译引用内容。双语对照时，先原文引用块再译文引用块。

## 其他翻译要求

8. 严格保持 Markdown 格式不变，包括标题、链接、图片引用等。
9. 仅翻译文字内容，保留所有 Markdown 语法和文件名。
10. 删除空链接、不必要的字符和如行末的 `\`。页码已由 convert.py 处理，不要再删除独立的数字行。
11. 保证格式和语义准确，翻译内容自然流畅。
12. 只输出双语对照的正文内容，不要有任何说明、提示、注释或对话内容。
13. 表达清晰简洁，不要使用复杂的句式。请严格按顺序翻译，不要跳过任何内容。
14. 必须保留所有图片引用，包括所有 `![alt](path)` 格式的图片引用必须完整保留，图片文件名和路径不要修改。
15. 原始 HTML 标签（如 `<img alt="..." />`）必须保持合法：翻译 `alt`、`title` 等属性值内部文本时，`"` 替换为 `"` `"`，`'` 替换为 `'` `'`，`<` 替换为 `&lt;`，`>` 替换为 `&gt;`，`&` 替换为 `&amp;`。不要修改 `src`、`href` 等结构性属性。
16. {CUSTOM_INSTRUCTIONS if provided}
17. 术语一致性：以下术语必须严格使用指定译法，不要自行变换。表格中"原文"列**或"别名"列**任一形式出现在正文中时，都必须翻译为"译文"列对应的形式。

{TERM_TABLE}

邻居上下文（只读，不要翻译，不要写入输出，只用于判断代词、性别、别名和跨 chunk 指代；为空则省略）:

{NEIGHBOR_CONTEXT}

## 双语输出示例

源文本：
```markdown
# Chapter 1: Introduction

This book is about data structures. We will cover trees, graphs, and hash tables.

## 1.1 Binary Trees

A binary tree is a tree data structure where each node has at most two children.
```

输出：
```markdown
# Chapter 1: Introduction / 第一章：引言

This book is about data structures. We will cover trees, graphs, and hash tables.

本书讲述数据结构。我们将涵盖树、图和哈希表。

## 1.1 Binary Trees / 1.1 二叉树

A binary tree is a tree data structure where each node has at most two children.

二叉树是一种树形数据结构，其中每个节点最多有两个子节点。
```

## 待翻译的 Markdown 源文本

---

### 第五步：验证完整性并重试

所有批次完成后，检查每个源分块是否有对应的输出文件。

如果有缺失，重试 — 每个缺失分块作为自己的子代理。每个分块最多 2 次尝试（初始 + 1 次重试）。

同时读取 `manifest.json` 并验证：
- 每个 chunk id 都有对应的输出文件
- 没有输出文件为空（0 字节）或空白（纯空白字符）

### 第六步：翻译书名

读取临时目录中的 `config.txt` 获取 `original_title` 字段。

将书名翻译为目标语言。对于中文，用书名号包裹：`《翻译后的书名》`。

### 第七步：后处理 — 合并并构建（同格式输出）

确定输入文件的格式（从 `config.txt` 中的 `input_file` 字段获取扩展名），
仅生成与输入相同格式的输出。

根据输入格式确定 `--format` 参数：
- 输入 `.epub` → `--format .epub`
- 输入 `.pdf` → `--format .pdf`
- 输入 `.docx` → `--format .docx`

从原始文件名提取词干（不含扩展名），构建导出名称：`{原书文件名}-{后缀}`。
后缀根据目标语言确定：
- `zh` → `英中双语`
- `en` → `bilingual`
- 其他 → `bilingual`

运行构建脚本：

```bash
python "{SKILL_DIR}/scripts/merge_and_build.py" \
  --temp-dir "<temp_dir>" \
  --title "<translated_title>" \
  --format ".epub" \
  --export-name "{原书文件名}-英中双语" \
  --cleanup
```

如果用户提供了 EPUB 封面图片，添加 `--cover "<cover_path>"`。
`--cleanup` 标志在构建成功后删除中间文件。如果用户希望保留中间文件，省略 `--cleanup`。

脚本在临时目录中生成：
- `output.md` — 合并后的双语 Markdown
- `book.html` — 网页版（带浮动目录）
- `book_doc.html` — 电子书版 HTML
- `book.{ext}` — 与输入同格式的最终文件
- `{原书文件名}-英中双语.{ext}` — 用户面向的导出副本

### 第八步：报告结果

告知用户：
- 输出文件的位置（`{原书文件名}-英中双语.{ext}` 的完整路径）
- 翻译了多少个分块
- 翻译后的书名
- 列出生成的输出文件及其大小
- 任何格式生成失败的信息

## 参考文件

| 文件 | 职责 |
|------|------|
| `scripts/convert.py` | PDF/DOCX/EPUB → Markdown 分块（经 Calibre HTMLZ） |
| `scripts/manifest.py` | 分块清单：SHA-256 跟踪和合并校验 |
| `scripts/glossary.py` | 术语表管理：为每个分块生成术语表，确保全书术语一致 |
| `scripts/chunk_context.py` | 只读的上一个/下一个分块摘录，用于子代理提示词 |
| `scripts/merge_and_build.py` | 合并双语分块 → HTML → DOCX/EPUB/PDF |
| `scripts/calibre_html_publish.py` | Calibre 封装，用于格式转换 |
| `scripts/template.html` | 网页 HTML 模板（带浮动目录） |
| `scripts/template_ebook.html` | 电子书 HTML 模板 |

## 使用方法

### 基本用法

```
帮我把这本书翻译成中文：D:/Books/alice.epub
```

或指定输出位置和语言：

```
请将 D:/Books/alice.epub 翻译为中文双语版，临时文件放到 D:/tmp
```

### 输出

- `{原书文件名}-英中双语.{ext}` — 双语对照的最终图书文件（与输入同格式）
- `{原书文件名}_temp/` — 临时工作目录（含中间文件，除非使用 `--cleanup`）

## 与原版的区别

本 skill 改编自 [deusyu/translate-book](https://github.com/deusyu/translate-book)（Claude Code Skill），主要变化：

1. **双语对照输出**：翻译提示词改为输出原文段落 + 译文段落逐段交替，而非纯译文
2. **同格式输出**：仅生成与输入格式相同的输出文件（原版生成所有格式）
3. **文件名后缀**：输出文件添加 `-英中双语` 后缀（原版使用 `book.*` 通用名）
4. **WorkBuddy 适配**：使用 WorkBuddy 的 Task 工具（团队模式）进行并行翻译，替代 Claude Code 的 Agent 工具
5. **简化流程**：移除了子代理元数据反馈循环（meta/merge_meta/run_state），保留术语表和邻居上下文核心功能
