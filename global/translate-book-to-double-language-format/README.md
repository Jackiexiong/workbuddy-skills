# translate-book-to-double-language-format — 整本书双语翻译助手

将 PDF/DOCX/EPUB 格式的整本书翻译为指定语言，输出**双语对照**版本（原文段落 + 译文段落逐段排列）。
使用并行子代理分块翻译，支持术语一致性和断点续译。输出保持与输入相同的格式。

> 改编自 [deusyu/translate-book](https://github.com/deusyu/translate-book)（Claude Code Skill），
> 适配 WorkBuddy 平台，增加双语对照输出和同格式输出功能。
>
> ⚡ **性能优化**：智能分块算法，短段落书籍翻译效率提升 59%！

---

## 目录

- [功能特性](#功能特性)
- [前置依赖](#前置依赖)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [工作原理](#工作原理)
- [双语输出格式](#双语输出格式)
- [高级用法](#高级用法)
- [性能优化](#性能优化)
- [故障排除](#故障排除)
- [文件结构](#文件结构)
- [与原版的区别](#与原版的区别)
- [许可证](#许可证)

---

## 功能特性

- **双语对照输出** — 每个原文段落后紧跟译文段落，标题显示为 `原文 / 译文`
- **同格式输出** — 输入 EPUB → 输出 EPUB；输入 PDF → 输出 PDF；输入 DOCX → 输出 DOCX
- **并行子代理** — 每批 8 个并发翻译器，每个拥有隔离的上下文
- **智能分块优化** — 自动分析段落特点，动态调整分块大小，减少 API 调用
- **术语一致性** — 翻译前构建术语表，全书统一专有名词译法
- **邻居上下文** — 每个分块可看到相邻分块的只读摘录，用于代词和实体消歧
- **清单校验** — SHA-256 哈希跟踪，防止过期或损坏的输出被合并
- **断点续译** — 中断后重运行跳过已完成分块
- **多语言** — zh、en、ja、ko、fr、de、es（可扩展）

---

## 前置依赖

### 必须安装

| 软件 | 用途 | 下载地址 |
|------|------|---------|
| **Calibre** | 格式转换核心 | https://calibre-ebook.com/download |
| **Pandoc** | HTML↔Markdown 转换 | https://pandoc.org/installing.html |
| **Python 3** (3.7+) | 运行脚本 | https://www.python.org/downloads/ |

### Python 依赖包

```bash
pip install pypandoc beautifulsoup4 markdown
```

---

## 快速开始

### 🚀 5 分钟快速上手指南

（更详细说明请参考 [`QUICKSTART.md`](QUICKSTART.md)）

#### 步骤 1：在 WorkBuddy 中安装技能

1. 将此文件夹复制到 WorkBuddy 的技能目录（如 `~/.workbuddy/skills/`）
2. 在 WorkBuddy 中刷新技能列表

或直接在当前位置通过 WorkBuddy 的"从本地文件夹导入"功能导入此技能。

#### 步骤 2：检查环境（重要！）

**Windows 用户：**
```cmd
# 双击运行或在命令行执行
install_skill.bat
```

**macOS/Linux 用户：**
```bash
chmod +x install_skill.sh
./install_skill.sh
```

或手动运行检查：
```bash
python check_env.py
```

确保所有依赖都显示为 `[OK]`。

#### 步骤 3：开始翻译！

在 WorkBuddy 中说：

```
帮我把这本书翻译成中文：D:/Books/alice.epub
```

技能会自动处理完整流水线！

---

## 详细使用说明

### 在 WorkBuddy 中的使用方式

#### 基本用法示例

| 场景 | 在 WorkBuddy 中说 |
|------|------------------|
| 翻译 EPUB | `把这本书翻译成中文：D:/Books/mybook.epub` |
| 翻译 PDF | `请翻译这个 PDF 文件：C:/Documents/report.pdf` |
| 翻译 DOCX | `将文档翻译为英文双语版：/Users/you/Documents/article.docx` |
| 指定临时目录 | `翻译这本书，临时文件放到 D:/tmp` |
| 自定义翻译风格 | `请将这本书翻译得更口语化，目标语言中文` |

#### 支持的输入格式

- `.epub` — 电子书
- `.pdf` — PDF 文档
- `.docx` — Word 文档

#### 输出格式说明

输出文件会自动：
- 与输入保持相同格式
- 文件名添加 `-英中双语` 后缀（目标语言为中文时）
- 例如：`mybook.epub` → `mybook-英中双语.epub`

### 工作流程详解

#### 第一阶段：预处理（自动执行）

```
输入文件 → Calibre 转换 → HTML → Markdown → 智能分块
```

当您提供图书文件后，技能会：
1. 使用 Calibre 将其转换为 HTMLZ（中间格式）
2. 提取并清理内容为 Markdown
3. **智能分析段落特点**，自动决定最佳分块大小
4. 将内容分割为多个 `chunk0001.md`、`chunk0002.md` 等

**优化说明**：
- 短段落多的书会自动使用更大的分块（15000 字符）
- 正常段落的书使用 12000 字符分块
- 这可以显著减少 API 调用次数！

#### 第二阶段：术语表构建（推荐，但可选）

如果临时目录中没有 `glossary.json`，技能会：
1. 采样几个代表性分块
2. 提取专有名词、人名、地名、技术术语等
3. 构建术语表并翻译
4. 统计每个术语在全书中的出现频率

**手动编辑术语表**：
您可以在翻译开始前或中断时编辑 `glossary.json` 来修正翻译。
已存在的术语表不会被覆盖。

#### 第三阶段：并行翻译

每个分块由一个独立子代理翻译：
- 每批最多 8 个并发（可调整）
- 每个子代理拥有全新上下文窗口，避免累积
- 自动注入术语表和邻居上下文
- 严格按照双语对照格式输出

**邻居上下文**：每个子代理能看到上一个分块末尾约 300 字符和下一个分块开头约 300 字符，用于代词和实体消歧。

#### 第四阶段：校验与合并

翻译完成后：
1. 校验所有分块的完整性（SHA-256 哈希）
2. 按顺序合并所有分块
3. 转换为带目录的 HTML
4. 构建最终输出文件（与输入同格式）

#### 第五阶段：输出交付

最终输出在临时目录中：
- `{原书名}-英中双语.epub` — 最终双语图书 ✅
- `output.md` — 合并后的双语 Markdown
- `book.html` — 网页版（带浮动目录）
- `book_doc.html` — 电子书版 HTML

### 详细使用示例

#### 示例 1：基本翻译

**输入**：
```
帮我把这本书翻译成中文：D:/Books/The_House_on_Mango_Street.epub
```

**输出**：
```
✅ 翻译完成！
- 输出文件：D:/Books/The_House_on_Mango_Street_temp/The_House_on_Mango_Street-英中双语.epub
- 翻译分块：11 个
- 书名翻译：The House on Mango Street / 《芒果街上的小屋》
```

#### 示例 2：指定临时目录

**输入**：
```
请将 D:/Books/mybook.epub 翻译为中文，临时文件放到 D:/temp
```

#### 示例 3：翻译为其他语言

**输入**：
```
把这个 PDF 翻译为日语：C:/Documents/report.pdf
```

#### 示例 4：自定义翻译指导

**输入**：
```
请将这本书翻译得更正式、更书面化：/Users/you/Documents/article.docx
```

---

## 工作原理

```
输入 (PDF/DOCX/EPUB)
  │
  ▼
Calibre ebook-convert → HTMLZ → HTML → Markdown
  │
  ▼
┌─────────────────────────────┐
│  智能内容分析               │ ← 新增！自动分析段落特点
│  - 段落长度统计             │
│  - 段落数量统计             │
│  - 决定最佳分块大小         │
└─────────────────────────────┘
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

---

## 双语输出格式

翻译后的文档采用**段落级双语对照**：

```markdown
# Chapter 1: Introduction / 第一章：引言

This book is about data structures. We will cover trees, graphs, and hash tables.

本书讲述数据结构。我们将涵盖树、图和哈希表。

## 1.1 Binary Trees / 1.1 二叉树

A binary tree is a tree data structure where each node has at most two children.

二叉树是一种树形数据结构，其中每个节点最多有两个子节点。
```

**格式规则**：
- **段落**：原文段落 → 空行 → 译文段落 → 空行
- **标题**：`原文标题 / 译文标题`（同一行，保持 Markdown 层级）
- **代码块**：保持原样不翻译
- **图片**：保持 `![alt](path)` 格式不变，alt 文本可翻译
- **表格**：保持 Markdown 表格结构，翻译单元格内容
- **列表**：保持列表层级和标记，翻译列表项文字
- **引用块**：保持 `>` 标记，翻译引用内容

---

## 高级用法

### 手动调整分块大小

如果您想控制分块大小，可以在临时目录生成后调整 `config.txt`，或直接使用 `convert.py`：

```bash
# 使用更大的分块（20000 字符）
python scripts/convert.py "mybook.epub" --chunk-size 20000
```

### 调整并发数

默认每批 8 个并发翻译。如果 API 有限制或系统较慢，可以调整：

编辑分块翻译提示词，在 WorkBuddy 中说：
```
翻译这本书，但每批只启动 4 个并发子代理
```

### 自定义术语表

如果您对某些术语的翻译有特殊要求：

1. 让技能运行到术语表生成完成（看到 `glossary.json` 出现）
2. 暂停，手动编辑 `{书名}_temp/glossary.json`
3. 继续翻译

术语表格式：
```json
{
  "version": 2,
  "terms": [
    {
      "id": "Manhattan",
      "source": "Manhattan",
      "target": "曼哈顿",
      "category": "place",
      "aliases": [],
      "frequency": 12
    }
  ]
}
```

### 断点续译

如果翻译中途停止（网络断开、程序崩溃等）：
- 重新在 WorkBuddy 中说同样的命令
- 技能会自动检测已完成的分块并跳过它们
- 继续翻译剩余分块

### 清理临时文件

翻译完成后，如果您想节省空间：
- 在 WorkBuddy 中要求清理
- 或手动删除 `{书名}_temp/` 目录（保留最终输出文件）

---

## 性能优化

### 智能分块算法

此功能在 v0.1.1 中新增，可以显著提升翻译效率：

| 书籍类型 | 优化前 | 优化后 | 节省 |
|---------|--------|--------|------|
| 短段落多 | 27 个分块 | 11 个分块 | **59%** ↓ |
| 正常段落 | 22 个分块 | 11-13 个分块 | **40-50%** ↓ |

**算法说明**：
1. 分析段落平均长度
2. 统计段落总数
3. 如果平均段落 < 300 字符且段落 > 200：使用 15000 字符分块
4. 如果平均段落 > 1000 字符：使用 10000 字符分块
5. 其他情况：使用 12000 字符分块
6. 同时优化标题分割策略，只有内容足够时才在标题处分割

### 优化效果验证

使用两本不同特点的书测试：

1. **The House on Mango Street**（正常段落小说）
   - 优化前：22 个分块
   - 优化后：11 个分块
   - 节省：50%

2. **Taboo Erotica Vol.1**（极短段落，1000+ 段）
   - 优化前：27 个分块
   - 优化后：11 个分块
   - 节省：59%

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Calibre ebook-convert not found` | Calibre 未安装或不在 PATH | 1. 下载安装 Calibre<br>2. 重启终端<br>3. 运行 `check_env.py` 验证 |
| `Pandoc not found` | Pandoc 未安装 | 下载安装 Pandoc，重启终端 |
| `ImportError: No module named ...` | Python 依赖未安装 | 运行 `pip install pypandoc beautifulsoup4 markdown` |
| `Manifest validation failed` | 源分块已更改 | 重新运行 `convert.py` 或删除临时目录重新开始 |
| `was created from different source bytes` | 临时目录属于不同源文件 | 删除临时目录或使用新的 `--temp-root` |
| `Blank output` / `Empty output` | 子代理写入了空白分块 | 重新运行技能，会自动重译该分块 |
| 翻译不完整 | 翻译中途停止 | 重新运行技能 — 它会从停止处恢复 |
| PDF 生成失败 | Calibre PDF 输出问题 | 确保 Calibre 已完整安装，包含 PDF 支持 |
| 图片丢失或损坏 | 图片路径问题 | 检查临时目录的 `images/` 文件夹，确保图片文件完整 |
| 术语翻译不一致 | 术语表问题 | 手动编辑 `glossary.json` 修正译法，重新运行合并步骤 |

### 获取帮助

运行环境检查：
```bash
python check_env.py
```

这会列出所有依赖项的状态。

---

## 文件结构

```
translate-book-to-double-language-format/
├── SKILL.md                          # WorkBuddy skill 定义 — 编排完整流水线
├── _meta.json                        # 技能元数据（版本、发布时间）
├── _skillhub_meta.json               # SkillHub 安装元数据
├── README.md                         # 本文档（详细说明）
├── QUICKSTART.md                     # 5 分钟快速开始指南
├── LICENSE                           # MIT 许可证
│
├── scripts/                          # 核心脚本
│   ├── convert.py                    # PDF/DOCX/EPUB → Markdown 分块（经 Calibre HTMLZ，含智能分块优化）
│   ├── manifest.py                   # 分块清单：SHA-256 跟踪和合并校验
│   ├── glossary.py                   # 术语表管理：为每个分块生成术语表
│   ├── chunk_context.py              # 只读邻居分块摘录，用于子代理提示词
│   ├── merge_and_build.py            # 合并双语分块 → HTML → DOCX/EPUB/PDF
│   ├── calibre_html_publish.py       # Calibre 封装，用于格式转换
│   ├── template.html                 # 网页 HTML 模板（带浮动目录）
│   └── template_ebook.html           # 电子书 HTML 模板
│
├── check_env.py                      # ✅ 环境检查工具
├── install_skill.bat                 # ✅ Windows 一键安装脚本
├── install_skill.sh                  # ✅ macOS/Linux 一键安装脚本
│
└── test/                             # 测试书籍（可选）
    ├── The House on Mango Street.epub
    └── Taboo Erotica Vol.1.epub
```

---

## 与原版的区别

本 skill 改编自 [deusyu/translate-book](https://github.com/deusyu/translate-book)，主要变化：

| 特性 | 原版（Claude Code） | 本版（WorkBuddy） |
|------|---------------------|-------------------|
| 输出格式 | 纯译文 | **双语对照**（原文 + 译文逐段） |
| 输出文件类型 | 生成所有格式（DOCX+EPUB+PDF） | **仅生成与输入相同的格式** |
| 文件名 | `book.*` 通用名 | `{原书名}-英中双语.{ext}` |
| 分块优化 | 固定 6000 字符 | **智能分块算法**，动态调整 |
| 效率 | 基准 | 短段落书提升 **59%** |
| 并行机制 | Claude Code Agent 工具 | WorkBuddy Task 工具（团队模式） |
| 元数据反馈 | 子代理 meta → glossary 自动合并 | 移除（简化流程，术语表手动编辑） |
| 选择性重译 | run_state.py 跟踪 | 移除（简化流程） |
| 安装工具 | 无 | ✅ 一键安装脚本 + 环境检查 |

---

## 版本历史

### v0.1.1
- ✅ 新增：智能分块算法，效率提升 59%
- ✅ 修复：Windows 下 EPUB 生成问题（python3 → sys.executable）
- ✅ 新增：一键安装脚本（Windows/macOS/Linux）
- ✅ 新增：环境检查工具
- ✅ 新增：快速开始指南
- ✅ 新增：WorkBuddy 元数据文件（`_meta.json`、`_skillhub_meta.json`）

### v0.1.0
- 初始版本，适配 WorkBuddy 平台

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 许可证

[MIT](LICENSE)

---

## 致谢

- 原版：[deusyu/translate-book](https://github.com/deusyu/translate-book)
- WorkBuddy 平台适配和优化
