#!/bin/bash
# WorkBuddy Skills 安装脚本 (macOS/Linux/Git Bash)
#
# 分类说明：
#   global       Agent 基础技能（人人必备）     — agent-self-improvement, document-skills, planning-files 等
#   office       办公文档类                      — docx, xlsx, pptx, pdf, 周报生成 等
#   coding       编程开发类                      — github, 代码审查, 全栈开发, 笔记搜索
#   design       前端设计类                      — Impeccable, frontend-design-3
#   search       搜索调研类                      — Deep Research, findskill
#   ai-creation  AI 创作类                      — image-generation, local-whisper, yt-dlp-downloader 等
#   custom       自定义通用技能（源自个人实践）— self-debug, req-doc-writer, 周报生成
#   teacher      教师用户                          — 备课助手, 试卷生成, 学生成绩分析
#
# 安装到用户级 (默认)：
#   bash install.sh                     # 全量安装（所有分类）
#   bash install.sh global office       # 只装 global + office
#   bash install.sh --skill coding/github  # 只装单个技能
#
# 安装到项目级：
#   bash install.sh --project global office
#
# 远程一键安装：
#   bash install.sh --clone global office

REPO_URL="https://github.com/bitcjm/workbuddy-skills.git"
CATEGORIES="global office coding design search ai-creation custom teacher"
COUNT=0
TARGET_DIR="$HOME/.workbuddy/skills"
INSTALL_MODE="categories"
SKILL_PATH=""
PROJECT_MODE=false
CLONE_MODE=false
CLEANUP_CLONE=false
CLONE_DIR=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --clone)
            CLONE_MODE=true
            shift
            ;;
        --project)
            PROJECT_MODE=true
            TARGET_DIR=".workbuddy/skills"
            shift
            ;;
        --skill)
            INSTALL_MODE="skill"
            shift
            SKILL_PATH="$1"
            shift
            ;;
        *)
            break
            ;;
    esac
done

SELECTED_CATEGORIES=("$@")

echo "======================================="
echo "  WorkBuddy Skills 安装脚本"
echo "======================================="
echo ""

# ── Clone 模式 ──
if [ "$CLONE_MODE" = true ]; then
    CLONE_DIR=$(mktemp -d workbuddy-skills-XXXXXX)
    echo "⬇️  正在从 GitHub 克隆仓库..."
    if ! git clone --depth 1 "$REPO_URL" "$CLONE_DIR" 2>&1; then
        echo "❌ 克隆失败，请检查网络连接"
        rm -rf "$CLONE_DIR"
        exit 1
    fi
    SKILLS_DIR="$CLONE_DIR"
    CLEANUP_CLONE=true
    echo "✅ 克隆完成: $CLONE_DIR"
    echo ""
else
    SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

# ── 单个技能安装 ──
if [ "$INSTALL_MODE" = "skill" ]; then
    if [ -z "$SKILL_PATH" ]; then
        echo "❌ 请指定技能路径，格式: --skill <分类>/<技能名>"
        echo "   示例: --skill coding/github"
        [ "$CLEANUP_CLONE" = true ] && rm -rf "$CLONE_DIR"
        exit 1
    fi

    SKILL_FULL_PATH="$SKILLS_DIR/$SKILL_PATH"
    SKILL_NAME="$(basename "$SKILL_PATH")"
    TARGET="$TARGET_DIR/$SKILL_NAME"

    if [ ! -d "$SKILL_FULL_PATH" ]; then
        echo "❌ 技能不存在: $SKILL_PATH"
        [ "$CLEANUP_CLONE" = true ] && rm -rf "$CLONE_DIR"
        exit 1
    fi

    mkdir -p "$TARGET_DIR"
    mkdir -p "$TARGET"

    if [ -d "$TARGET" ] && [ "$(ls -A "$TARGET" 2>/dev/null)" ]; then
        echo "🔄 更新: $SKILL_PATH → $TARGET"
    else
        echo "📦 安装: $SKILL_PATH → $TARGET"
    fi

    cp -r "$SKILL_FULL_PATH/"* "$TARGET/" 2>/dev/null
    cp -r "$SKILL_FULL_PATH/".[!.]* "$TARGET/" 2>/dev/null
    ((COUNT++))

    if [ "$CLEANUP_CLONE" = true ]; then
        echo ""
        echo "🧹 清理临时克隆目录: $CLONE_DIR"
        rm -rf "$CLONE_DIR"
    fi

    echo ""
    echo "✅ 安装完成！共处理 $COUNT 个技能"
    exit 0
fi

# ── 分类安装 ──
mkdir -p "$TARGET_DIR"

# 未指定分类 → 安装全部
if [ ${#SELECTED_CATEGORIES[@]} -eq 0 ]; then
    SELECTED_CATEGORIES=($CATEGORIES)
fi

for cat in "${SELECTED_CATEGORIES[@]}"; do
    CAT_PATH="$SKILLS_DIR/$cat"
    if [ ! -d "$CAT_PATH" ]; then
        echo "⚠️  分类不存在: $cat"
        continue
    fi

    echo "📁 [$cat]"
    for skill_dir in "$CAT_PATH"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name="$(basename "$skill_dir")"
        target="$TARGET_DIR/$skill_name"
        mkdir -p "$target"
        if [ "$(ls -A "$target" 2>/dev/null)" ]; then
            echo "  🔄 更新: $skill_name"
        else
            echo "  📦 安装: $skill_name"
        fi
        cp -r "$skill_dir"* "$target/" 2>/dev/null
        cp -r "$skill_dir".[!.]* "$target/" 2>/dev/null
        ((COUNT++))
    done
    echo ""
done

# 清理 clone 目录
if [ "$CLEANUP_CLONE" = true ]; then
    echo "🧹 清理临时克隆目录: $CLONE_DIR"
    rm -rf "$CLONE_DIR"
    echo ""
fi

echo "✅ 安装完成！共处理 $COUNT 个技能"
if [ "$PROJECT_MODE" = true ]; then
    echo "📍 安装位置: 项目级 (.workbuddy/skills/)"
else
    echo "📍 安装位置: 用户级 (~/.workbuddy/skills/)"
fi
