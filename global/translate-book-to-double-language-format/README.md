# translate-book-to-double-language-format — 整本书双语翻译助手

将 PDF/DOCX/EPUB 格式的整本书翻译为指定语言，输出**双语对照**版本（原文段落 + 译文段落逐段排列）。
使用并行子代理分块翻译，支持术语一致性和断点续译。输出保持与输入相同的格式。

> 改编自 [deusyu/translate-book](https://github.com/deusyu/translate-book)（Claude Code Skill），
> 适配 WorkBuddy 平台，增加双语对照输出和同格式输出功能。

---

## 工作原理

```
输入 (PDF/DOCX/EPUB)
  │
  ▼
Calibre ebook-convert → HTMLZ → HTML → Markdown
  │
  ▼
分块 (chunk0001.md, chunk0002.md, ...)
  │  manifest.json 跟踪分块哈希
  ▼
构建术语表 (glossary.json)
  │  确保全书专有名词翻译一致
  ▼
并行子代理翻译 (每批 8 个并发)
  │  每个子代理：读取 1 个分块 → 输出双语对照 → 写入 output_chunk*.md
  │  批处理以遵守 API 速率限制
  ▼
校验 (manifest 哈希检查，源↔输出 1:1 匹配)
  │
  ▼
合并 → Pandoc → HTML (带目录) → Calibre → 与输入同格式输出
  │
  ▼
{原书文件名}-英中双语.{ext}
```

每个分块由一个独立子代理翻译，拥有全新的上下文窗口。这避免了在单个会话中翻译整本书时的上下文累积和输出截断问题。

## 核心特性

- **双语对照输出** — 每个原文段落后紧跟译文段落，标题显示为 `原文 / 译文`
- **同格式输出** — 输入 EPUB → 输出 EPUB；输入 PDF → 输出 PDF；输入 DOCX → 输出 DOCX
- **并行子代理** — 每批 8 个并发翻译器，每个拥有隔离的上下文
- **术语一致性** — 翻译前构建术语表，全书统一专有名词译法
- **邻居上下文** — 每个分块可看到相邻分块的只读摘录，用于代词和实体消歧
- **清单校验** — SHA-256 哈希跟踪，防止过期或损坏的输出被合并
- **断点续译** — 中断后重运行跳过已完成分块
- **多语言** — zh、en、ja、ko、fr、de、es（可扩展）

## 前置依赖

- **Calibre** — `ebook-convert` 命令必须可用（[下载](https://calibre-ebook.com/)）
- **Pandoc** — 用于 HTML↔Markdown 转换（[下载](https://pandoc.org/)）
- **Python 3**，安装以下包：

  ```bash
  pip install pypandoc beautifulsoup4 markdown
  ```

## 快速开始

### 1. 安装 skill

```powershell
# 从本仓库安装
.\install.ps1 global

# 或只安装此 skill
.\install.ps1 -Skill global/translate-book-to-double-language-format
```

### 2. 翻译一本书

在 WorkBuddy 中说：

```
帮我把这本书翻译成中文：D:/Books/alice.epub
```

或指定更多参数：

```
请将 D:/Books/alice.epub 翻译为中文双语版，临时文件放到 D:/tmp
```

技能自动处理完整流水线 — 转换、分块、并行翻译、校验、合并、构建输出格式。

### 3. 查找输出

所有文件在 `{书名}_temp/` 目录中：

| 文件 | 说明 |
|------|------|
| `{原书名}-英中双语.epub` | 双语对照电子书（与输入同格式） |
| `output.md` | 合并后的双语 Markdown |
| `book.html` | 网页版（带浮动目录） |

## 双语输出格式

翻译后的文档采用**段落级双语对照**：

```markdown
# Chapter 1: Introduction / 第一章：引言

This book is about data structures.

本书讲述数据结构。

## 1.1 Binary Trees / 1.1 二叉树

A binary tree is a tree data structure.

二叉树是一种树形数据结构。
```

- **段落**：原文段落 → 空行 → 译文段落 → 空行
- **标题**：`原文标题 / 译文标题`（同一行）
- **代码块/图片/表格**：保持原样不翻译

## 文件结构

| 文件 | 职责 |
|------|------|
| `SKILL.md` | WorkBuddy skill 定义 — 编排完整流水线 |
| `scripts/convert.py` | PDF/DOCX/EPUB → Markdown 分块（经 Calibre HTMLZ） |
| `scripts/manifest.py` | 分块清单：SHA-256 跟踪和合并校验 |
| `scripts/glossary.py` | 术语表管理：为每个分块生成术语表 |
| `scripts/chunk_context.py` | 只读邻居分块摘录，用于子代理提示词 |
| `scripts/merge_and_build.py` | 合并双语分块 → HTML → DOCX/EPUB/PDF |
| `scripts/calibre_html_publish.py` | Calibre 封装，用于格式转换 |
| `scripts/template.html` | 网页 HTML 模板（带浮动目录） |
| `scripts/template_ebook.html` | 电子书 HTML 模板 |

## 术语表

翻译前，技能会采样几个分块，提取专有名词和领域术语，构建 `glossary.json`：

```json
{
  "version": 2,
  "terms": [
    {"id": "Manhattan", "source": "Manhattan", "target": "曼哈顿",
     "category": "place", "aliases": [], "frequency": 12}
  ],
  "high_frequency_top_n": 20
}
```

术语表是**可手动编辑**的。在两次运行之间编辑 `glossary.json` 修正翻译；已存在的 `glossary.json` 不会被覆盖。每个子代理的提示词中会注入与其分块相关的术语表，作为硬性约束。

## 与原版的区别

本 skill 改编自 [deusyu/translate-book](https://github.com/deusyu/translate-book)，主要变化：

| 特性 | 原版（Claude Code） | 本版（WorkBuddy） |
|------|---------------------|-------------------|
| 输出格式 | 纯译文 | **双语对照**（原文 + 译文逐段） |
| 输出文件类型 | 生成所有格式（DOCX+EPUB+PDF） | **仅生成与输入相同的格式** |
| 文件名 | `book.*` 通用名 | `{原书名}-英中双语.{ext}` |
| 并行机制 | Claude Code Agent 工具 | WorkBuddy Task 工具（团队模式） |
| 元数据反馈 | 子代理 meta → glossary 自动合并 | 移除（简化流程，术语表手动编辑） |
| 选择性重译 | run_state.py 跟踪 | 移除（简化流程） |

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| `Calibre ebook-convert not found` | 安装 Calibre 并确保 `ebook-convert` 在 PATH 中 |
| `Manifest validation failed` | 源分块已更改 — 重新运行 `convert.py` |
| `was created from different source bytes` | 临时目录属于不同源文件 — 删除临时目录或使用新的 `--temp-root` |
| `Blank output` / `Empty output` | 子代理写入了空白分块 — 重新运行技能重译该分块 |
| 翻译不完整 | 重新运行技能 — 它会从停止处恢复 |
| PDF 生成失败 | 确保 Calibre 已安装 PDF 输出支持 |

## 许可证

[MIT](LICENSE)
