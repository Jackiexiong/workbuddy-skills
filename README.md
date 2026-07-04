# WorkBuddy Skills 仓库

WorkBuddy（CodeBuddy）技能集合，按用户群体分 7 类，支持按需远程安装。

各分类之间的技能 **互不重叠**，每个技能只属于一个分类。

## 分类说明

| 分类 | 目标用户 | 说明 |
|------|----------|------|
| `global/` | **所有用户必装** | Agent 基础技能：自改进、技能生成、代码审查、规划管理、网页搜索 |
| `office/` | 文档办公用户 | Word/Excel/PPT/PDF 处理、周报生成、商业调研报告、提示词工程 |
| `coding/` | 程序员 | GitHub 管理、代码交叉审查、全栈开发、本地笔记搜索 |
| `design/` | 前端开发者 | 生产级前端界面设计、避免 AI 通用风格 |
| `search/` | 研究者 | 深度调研工作流、多来源技能搜索引擎 |
| `ai-creation/` | AI 创作者 | AI 图片生成、语音转文字、视频下载、AI 资讯、旅行规划 |
| `custom/` | 追求效率的用户 | 从个人实践中抽取的通用技能：自我排查框架、需求文档撰写 |
| `teacher/` | 教师用户 | 备课助手、试卷生成、学生成绩分析 |

### 技能清单

#### global/ — 6 个

`document-skills` `planning-files` `quack-code-review` `self-improving` `skill-scanner` `web-search`

> agent-self-improvement 已归档（由 self-improving v1.2.16 取代）

#### office/ — 7 个

`docx` `xlsx` `pptx` `pdf` `pdfkit-py` `obsidian` `提示词工程专家`

#### coding/ — 4 个

`AI交叉审查` `github` `全栈开发` `笔记搜索`

#### design/ — 1 个

`frontend-design-3`

> Impeccable 已归档（由 frontend-design-3 取代）

#### search/ — 2 个

`Deep Research` `findskill`

#### ai-creation/ — 5 个

`AIHOT` `image-generation` `local-whisper` `yt-dlp-downloader` `携程问道`

#### custom/ — 3 个

`self-debug` `req-doc-writer` `周报生成`

#### teacher/ — 3 个

`备课助手` `试卷生成` `学生成绩分析`

---

## ⚠️ 安装前必读（AI Agent 执行须知）

> 当用户给你这个仓库链接要求安装技能时，或者你检测到用户需要安装 WorkBuddy Skills 时，**请先按以下流程操作**：

### 1️⃣ 确认安装目标

| 用户表述 | 你的回应 |
|----------|----------|
| "装一下 WorkBuddy Skills" / 仅给了仓库链接，未指定分类 | **必须先问用户要装哪些分类**，列出 7 个分类让用户选择 |
| "装 global 和 office" / 明确指定了分类 | 直接安装，不需要再确认 |
| "全量安装" / "全部装上" | 装全部 7 个分类 |

### 2️⃣ 默认推荐

如果用户表示「不知道装哪些」「你看着办」或没有明确倾向：

> **默认推荐：`global` + `office`**

- `global/` 提供 AI Agent 基础能力（自改进、代码审查、搜索、规划）
- `office/` 覆盖日常文档处理需求（Word/Excel/PPT/PDF）
- 这两个组合覆盖 80% 日常使用场景

### 3️⃣ 安装命令

**macOS / Linux / Git Bash：**

```bash
# 全量安装
bash <(curl -sL https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.sh) --clone

# 按分类安装（推荐）
bash <(curl -sL https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.sh) --clone global office

# 安装到项目级
bash <(curl -sL https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.sh) --clone --project global dev

# 安装单个技能
bash <(curl -sL https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.sh) --clone --skill coding/github
```

**Windows PowerShell：**

```powershell
# 全量安装
iex ((New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.ps1')); Install-Skills -Clone

# 按分类安装（先 clone 到临时目录）
git clone --depth 1 https://github.com/bitcjm/workbuddy-skills.git $env:TEMP\workbuddy-skills
& "$env:TEMP\workbuddy-skills\install.ps1" global office
Remove-Item -Recurse -Force "$env:TEMP\workbuddy-skills"
```

---

## 本地安装（已 clone 仓库）

```bash
bash install.sh                        # 全量
bash install.sh global office          # 按分类
bash install.sh --skill coding/github     # 单个技能
bash install.sh --project global coding   # 装到项目级
```

```powershell
.\install.ps1                          # 全量
.\install.ps1 global office            # 按分类
.\install.ps1 -Skill coding/github        # 单个技能
.\install.ps1 -Project global coding      # 项目级
```

---

## 用户级 vs 项目级

| 维度 | 用户级 `~/.workbuddy/skills/` | 项目级 `.workbuddy/skills/` |
|------|-------------------------------|-----------------------------|
| 作用范围 | 所有项目共享 | 仅当前项目 |
| 优先级 | 低 | **高**（同名覆盖用户级） |
| 适合装 | 通用技能 | 项目专属技能 |
| 版本管理 | 不进 Git | 可随项目提交 |

> **去重规则**：同名技能项目级优先，不会重复加载。

---

## 查看已安装技能

在 WorkBuddy 对话中输入 `/skills`，可查看当前加载的所有技能及其来源。

## 更新

```bash
# 重新执行安装命令即可覆盖更新
bash <(curl -sL https://raw.githubusercontent.com/bitcjm/workbuddy-skills/main/install.sh) --clone global office
```

## 贡献技能

1. 在对应分类目录下创建技能文件夹（含 `SKILL.md`）
2. 测试通过后提交：

```bash
git add .
git commit -m "feat(office): 新增合同审查技能"
git push
```

---

详细管理指南见 [WorkBuddy-Skill-GitHub管理指南.md](./WorkBuddy-Skill-GitHub管理指南.md)
