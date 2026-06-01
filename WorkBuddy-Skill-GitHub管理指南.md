# WorkBuddy Skills GitHub 管理指南

> 用 Git 管理你的 AI 技能，实现版本控制、分类组织、跨设备同步。

---

## 一、为什么需要 GitHub 管理 Skills？

WorkBuddy 的 Skills 存储在 `~/.workbuddy/skills/`（用户级全局）和各项目的 `.workbuddy/skills/`（项目级）。
单纯本地管理会遇到以下问题：

| 问题 | 说明 |
|------|------|
| ❌ 版本丢失 | 修改了 Skill 但忘了改了什么，改错了想回退也没办法 |
| ❌ 换机困难 | 换电脑后所有 Skills 要重新装、重新配 |
| ❌ 分类混乱 | 20+ 个 Skill 堆在一起，全局/领域混着，难以管理 |
| ❌ 无法协作 | 和别人共享 Skill 只能发压缩包，版本靠文件名 |
| ❌ 无发布渠道 | 自己写的好 Skill 没法让团队/社区使用 |

通过 GitHub 仓库管理 Skills，可以做到：

- ✅ **Git 版本控制** — 每次修改可追溯、可回退
- ✅ **分类分级** — 通用技能自动安装，领域技能按需选用
- ✅ **一键部署到新机** — `git clone + 一键安装脚本` 搞定
- ✅ **团队共享** — 同事 clone 仓库就能同步全部 Skills
- ✅ **CI/CD 自动化** — 提交后自动校验格式、发布到市场

---

## 二、仓库结构设计

建议按以下目录结构组织 Skill 仓库：

```
workbuddy-skills/
├── README.md                    # 仓库说明
├── install.sh                   # 一键安装脚本（macOS/Linux/Git Bash）
├── install.ps1                  # 一键安装脚本（Windows）
├── make-symlinks.sh             # 符号链接模式脚本（开发时直接用）
├── .github/
│   └── workflows/
│       └── skill-validate.yml   # CI：提交时自动校验 SKILL.md 格式
│
├── global/                      # ← Agent 基础技能（人人必备）
│   ├── agent-self-improvement/
│   ├── document-skills/
│   ├── planning-files/
│   ├── quack-code-review/
│   ├── self-improving/
│   ├── skill-scanner/
│   └── web-search/
│
├── office/                      # ← 办公文档领域
│   ├── docx/
│   ├── xlsx/
│   ├── pptx/
│   ├── pdf/
│   ├── pdfkit-py/
│   ├── obsidian/
│   ├── 周报生成/
│   ├── 业务调研报告撰写/
│   └── 提示词工程专家/
│
├── coding/                         # ← 编程开发领域
│   ├── AI交叉审查/
│   ├── github/
│   ├── 全栈开发/
│   └── 笔记搜索/
│
├── design/                      # ← 前端设计领域
│   ├── Impeccable（前端设计工具集）/
│   └── frontend-design-3/
│
├── search/                      # ← 搜索调研领域
│   ├── Deep Research/
│   └── findskill/
│
├── ai-creation/                 # ← AI 创作领域
│   ├── AIHOT/
│   ├── image-generation/
│   ├── local-whisper/
│   ├── yt-dlp-downloader/
│   └── 携程问道/
│
├── custom/                      # ← 自定义通用（从个人库抽取）
│   ├── self-debug/
│   └── req-doc-writer/
│
└── archive/                     # ← 不再维护的旧 Skill
    └── deprecated-skill/
        └── SKILL.md
```

### 分文件夹的推荐策略

| 领域目录 | 目标用户 | 示例 Skill |
|----------|----------|------------|
| `global/` | **所有用户必装** | agent-self-improvement, document-skills, planning-files, quack-code-review, self-improving, skill-scanner, web-search |
| `office/` | 文档办公用户 | docx/xlsx/pptx/pdf 处理、周报生成、业务调研报告、提示词工程 |
| `coding/` | 程序员 | 代码审查、GitHub 管理、全栈开发、笔记搜索 |
| `design/` | 前端开发者 | 前端设计工具集、免 AI 通用风界面 |
| `search/` | 研究者 | 深度调研、多来源技能搜索引擎 |
| `ai-creation/` | AI 创作者 | 图片生成、语音转文字、视频下载、旅行规划 |
| `custom/` | 追求效率的用户 | 自我排查框架、需求文档撰写（从个人库抽取的通用技能） |
| `archive/` | — | 不再使用的旧 Skill |

> 💡 **分类原则**：
> - `global/` — 每个 AI Agent 都应该有的基础能力
> - 领域目录 — 仅在相关场景下有用，按需安装
> - `custom/` — 源自个人实践但已提炼为通用方案，对所有人有价值
> - 各目录技能互不重叠，每个 Skill 只属于一个分类

---

## 三、SKILL.md 格式速查

SKILL.md 是 WorkBuddy 技能的核心描述文件，使用 YAML frontmatter + Markdown 正文。

### 基础模板

```markdown
---
name: my-skill-name
version: 1.0.0
description: |
  用英文写完整的触发条件和适用范围描述。
  TRIGGER when: xxx
  DO NOT TRIGGER when: xxx
description_zh: "简短的中文描述"
description_en: "Short English description"
license: MIT
allowed-tools:
  - Read
  - Write
  - Bash
metadata:
  category: coding
  author: "你的名字"
---

# 技能名称

技能的核心逻辑和用法说明...
```

### 常用 frontmatter 字段

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `name` | ✅ | 技能唯一标识，字母数字+中划线 | `deep-research` |
| `version` | ✅ | 语义化版本 | `1.0.0` |
| `description` | ✅ | 完整触发条件描述，用 `\n` 分行 | 见上 |
| `description_zh` | ✅ | 简短中文说明 | `"深度研究助手"` |
| `description_en` | ✅ | 简短英文说明 | `"Deep research assistant"` |
| `license` | ❌ | 开源协议 | `MIT` / `Apache-2.0` |
| `allowed-tools` | ❌ | 允许的技能可调用工具列表 | `[Read, Write, Bash]` |
| `metadata.category` | ❌ | 分类标签 | `coding` / `office` / `stock` |
| `metadata.version` | ❌ | 在 metadata 中标注版本（可选） | `1.0.0` |
| `disable` | ❌ | 安装后默认禁用 | `true` 或不写 |

---

## 四、核心操作命令

以下命令帮助你在本地和 GitHub 之间管理 Skills。

### 4.1 初始化仓库

```bash
# 1. 在 GitHub 上新建仓库（略）

# 2. 本地创建目录结构
mkdir -p workbuddy-skills/{global,office,coding,design,search,ai-creation,custom,archive}
cd workbuddy-skills

# 3. 初始化 Git 仓库
git init
git checkout -b main
```

---

### 4.2 将本地已安装 Skills 复制到仓库

```bash
# 基本操作：cp 单个 Skill
cp -r ~/.workbuddy/skills/web-search ./global/
cp -r ~/.workbuddy/skills/全栈开发 ./coding/
cp -r ~/.workbuddy/skills/业务调研报告撰写 ./office/

# 如果是 Windows Git Bash 注意路径格式
```

> ⚠️ **重要提醒**：
> - 使用 `cp` 复制而非 `mv` 移动，确保本地 WorkBuddy 仍能正常使用
> - 复制完成后，`.gitignore` 中不要排除本地的 `~/.workbuddy/skills/`

---

### 4.3 提交并推送到 GitHub

```bash
# 1. 查看状态
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "feat: 初始化技能仓库，分类整理全局/办公/炒股/编程技能"

# 4. 关联远程仓库
git remote add origin https://github.com/<你的用户名>/workbuddy-skills.git

# 5. 推送
git push -u origin main
```

---

### 4.4 日常修改和更新 Skill

```bash
# 场景：你修改了本地的某个 Skill，要同步到 GitHub

# 1. 把更新后的 Skill 复制到仓库
cp -r ~/.workbuddy/skills/周报生成 ./office/

# 2. 查看差异
git diff

# 3. 提交
git add ./office/周报生成
git commit -m "feat(office): 更新周报生成技能，优化表格格式"
git push
```

---

### 4.5 从仓库安装到新电脑

**方式一：一键复制脚本（推荐）**

新建 `install-all.sh`：

```bash
#!/bin/bash
# WorkBuddy Skills 一键安装脚本
# 将所有目录下的 Skill 复制到 ~/.workbuddy/skills/

SKILLS_DIR="$(dirname "$0")"
TARGET_DIR="$HOME/.workbuddy/skills"

# 遍历所有分类目录
for category in global office coding design search ai-creation custom; do
    if [ -d "$SKILLS_DIR/$category" ]; then
        for skill_dir in "$SKILLS_DIR/$category"/*/; do
            skill_name="$(basename "$skill_dir")"
            echo "📦 安装: $category/$skill_name"
            mkdir -p "$TARGET_DIR/$skill_name"
            cp -r "$skill_dir"* "$TARGET_DIR/$skill_name/"
        done
    fi
done

echo "✅ 全部安装完成！"
```

Windows PowerShell 版 `install-all.ps1`：

```powershell
# WorkBuddy Skills 一键安装脚本 (Windows)
$SkillsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = "$env:USERPROFILE\.workbuddy\skills"

$categories = @("global", "office", "coding", "design", "search", "ai-creation", "custom")

foreach ($cat in $categories) {
    $catPath = Join-Path $SkillsDir $cat
    if (Test-Path $catPath) {
        Get-ChildItem -Path $catPath -Directory | ForEach-Object {
            $skillPath = $_.FullName
            $skillName = $_.Name
            $target = Join-Path $TargetDir $skillName
            Write-Host "📦 安装: $cat/$skillName"
            if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }
            Copy-Item -Path "$skillPath\*" -Destination $target -Recurse -Force
        }
    }
}

Write-Host "✅ 全部安装完成！"
```

**方式二：符号链接模式（开发用，实时同步）**

新建 `make-symlinks.sh`：

```bash
#!/bin/bash
# 建立符号链接，仓库内修改实时反映到 WorkBuddy

SKILLS_DIR="$(dirname "$0")"
TARGET_DIR="$HOME/.workbuddy/skills"

for category in global office stock coding ai-creation; do
    if [ -d "$SKILLS_DIR/$category" ]; then
        for skill_dir in "$SKILLS_DIR/$category"/*/; do
            skill_name="$(basename "$skill_dir")"
            echo "🔗 链接: $category/$skill_name"
            ln -sfn "$skill_dir" "$TARGET_DIR/$skill_name"
        done
    fi
done

echo "✅ 符号链接建立完成！"
```

> ⚠️ Windows 下符号链接需要管理员权限，或使用 `mklink /D` 命令。
> 推荐 Windows 用户直接使用 方式一（复制）即可。

---

### 4.6 从仓库增量更新本地 Skills

```bash
# 当别人或自己在仓库中更新了 Skill，拉取后同步到本地

git pull
bash install-all.sh          # 方式一：全部覆盖安装
# 或者
bash make-symlinks.sh        # 方式二：重建符号链接
```

---

## 五、安装脚本的 .gitignore 建议

在仓库根目录创建 `.gitignore`：

```
# 操作系统临时文件
.DS_Store
Thumbs.db

# IDE 项目文件
.idea/
.vscode/
*.swp
*.swo

# 日志和临时文件
*.log
tmp/
```

---

## 六、进阶玩法

### 6.1 GitHub CI：自动校验 SKILL.md 格式

在 `.github/workflows/skill-validate.yml` 中：

```yaml
name: Validate Skills

on:
  push:
    paths:
      - '**/SKILL.md'
  pull_request:
    paths:
      - '**/SKILL.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check SKILL.md frontmatter
        run: |
          echo "检查所有 SKILL.md 文件是否存在必要字段..."
          errors=0
          while IFS= read -r file; do
            if ! head -20 "$file" | grep -q "^name:"; then
              echo "❌ $file: 缺少 name 字段"
              ((errors++))
            fi
            if ! head -20 "$file" | grep -q "^description:"; then
              echo "❌ $file: 缺少 description 字段"
              ((errors++))
            fi
          done < <(find . -name 'SKILL.md' -not -path './archive/*')
          if [ $errors -gt 0 ]; then
            echo "共 $errors 个错误"
            exit 1
          fi
          echo "✅ 所有 SKILL.md 格式正确"
```

### 6.2 使用 Tag 管理版本

```bash
# 发布版本时打 tag
git tag -a v1.0.0 -m "初始版本：15 个分类好的技能"
git push --tags

# 查看版本历史
git tag -l
```

### 6.3 基于分支管理不同版本

```bash
# 主分支：稳定版
git checkout main

# 开发分支：新增或修改 Skill 时
git checkout -b dev/new-skill

# 修改完成后合并回主分支
git checkout main
git merge dev/new-skill
```

### 6.4 快速导出/导入单个 Skill 包

```bash
# 导出某个 Skill 为 zip 包（上传到 WorkBuddy 市场用）
cd ~/.workbuddy/skills
zip -r ~/Desktop/周报生成.zip 周报生成/

# 在 WorkBuddy 中通过「添加技能 → 上传技能」导入这个 zip 包即可
```

---

## 七、本仓库的 Skills 分类一览

| 分类 | 包含 Skill |
|------|-------------|
| **global/ 基础必备** (6) | document-skills, planning-files, quack-code-review, self-improving, skill-scanner, web-search |
| **office/ 办公文档** (9) | docx, xlsx, pptx, pdf, pdfkit-py, obsidian, 周报生成, 业务调研报告撰写, 提示词工程专家 |
| **coding/ 编程开发** (4) | AI交叉审查, github, 全栈开发, 笔记搜索 |
| **design/ 前端设计** (1) | frontend-design-3 |
| **search/ 搜索调研** (2) | Deep Research, findskill |
| **ai-creation/ AI 创作** (5) | AIHOT, image-generation, local-whisper, yt-dlp-downloader, 携程问道 |
| **custom/ 自定义通用** (2) | self-debug, req-doc-writer |

---

## 八、完整操作流程速查

```bash
# 🚀 第一天：初始化
mkdir workbuddy-skills && cd workbuddy-skills
git init && git checkout -b main
mkdir -p {global,office,coding,design,search,ai-creation,custom,archive}
# 复制所有 Skill 到对应目录...
git add . && git commit -m "init"
git remote add origin <你的仓库URL>
git push -u origin main

# 📅 日常更新 Skill
cp -r ~/.workbuddy/skills/某技能 ./office/
git add . && git commit -m "update: 修改了什么" && git push

# 💻 换电脑/新环境
git clone <你的仓库URL>
cd workbuddy-skills
bash install-all.sh         # macOS/Linux
# 或
powershell -File install-all.ps1  # Windows
```

---

## 九、推荐创建 GitHub 仓库时填写的信息

| 项目 | 内容 |
|------|------|
| **仓库名** | `workbuddy-skills` 或 `my-workbuddy-skills` |
| **描述** | `WorkBuddy Skills 集合 — 基础通用 + 办公文档 + 编程开发 + 前端设计 + 搜索调研 + AI 创作 + 自定义通用` |
| **可见性** | 私有（个人用）/ 公开（分享给社区） |
| **README** | 直接引用本指南中的内容 |
| **Topics** | `workbuddy`, `skills`, `ai-agent`, `codebuddy` |
| **License** | MIT（推荐） |

---

## 十、常见问题

**Q：修改了本地 Skill 后，需要手动 cp 到仓库吗？**

A：是的。建议采用「修改本地 → 测试通过 → cp 到仓库 → commit & push」的工作流。
如果想省去 cp 步骤，可以用符号链接（方式二），仓库目录即本地目录。

**Q：仓库里的 Skill 和本地 .workbuddy/skills/ 会冲突吗？**

A：不会。仓库只是一个备份/分发源，WorkBuddy 读取的仍然是 `~/.workbuddy/skills/`。
两者独立，需要手动同步。

**Q：如何让团队也能用我的 Skill 仓库？**

A：把仓库设为公开，或者给团队成员 GitHub 访问权限。他们 clone 后运行安装脚本即可。

**Q：Skill 有二进制文件怎么办？**

A：如果 Skill 依赖脚本文件（如 Python/Node 脚本），将整个 Skill 目录放入仓库即可，
安装脚本会自动复制。超过 100MB 的大文件建议用 Git LFS。

---

*Happy Skilling! 🤖*