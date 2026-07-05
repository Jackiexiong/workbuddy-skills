# Git 操作与凭证管理指南

本文档提供本技能中 Git 操作的详细指南，包括认证方式、错误处理和批量操作优化。

---

## 一、认证方式

### URL 嵌入用户名密码

最适用于本技能场景（自动批量操作，无需交互）：

```bash
# 格式
git clone --depth 1 https://用户名:密码@github.com/用户/仓库.git

# 示例
git clone --depth 1 https://admin:MyPass123@github.com/student2021/student-management.git
```

### 注意事项

1. **特殊字符转义**：密码中含有 `@`、`#`、`/` 等特殊字符时需进行 URL 编码：

| 字符 | 编码 |
|------|------|
| `@` | `%40` |
| `#` | `%23` |
| `/` | `%2F` |
| `:` | `%3A` |
| `%` | `%25` |
| `空格` | `%20` |

2. **密码安全**：URL 中的密码可能会被记录到 Git 日志或 shell 历史中，建议操作完成后清理。

### 其他认证方式（可选支持）

#### SSH 密钥

如果设备已配置 SSH 密钥，可以直接使用：

```bash
git clone --depth 1 git@github.com:student/repo.git
```

#### Git 凭证管理器

```bash
# 设置全局凭证
git config --global credential.helper store
# 首次手动输入后，后续自动使用
git clone https://github.com/student/repo.git
```

---

## 二、批量操作规范

### 工作目录管理

```bash
# 创建工作目录
WORK_DIR="./_code_review_workspace"
mkdir -p "$WORK_DIR"

# 为每位学生创建子目录（格式：学号_姓名）
STUDENT_DIR="$WORK_DIR/2024001_张三"
mkdir -p "$STUDENT_DIR"
```

### 克隆命令模板

```bash
# 替换占位符
REPO_URL="https://${GIT_USER}:${GIT_PASS}@${REPO_HOST}/${REPO_PATH}"
git clone --depth 1 "$REPO_URL" "$WORK_DIR/${STUDENT_ID}_${STUDENT_NAME}"
```

### 清理工作目录

```bash
# 评分完成后清理
rm -rf "$WORK_DIR"

# 或仅保留问题仓库用于复查
```

---

## 三、错误处理

### 常见错误与处理策略

| 错误信息 | 含义 | 处理方式 |
|---------|------|---------|
| `Repository not found` | 仓库不存在 | 备注"仓库地址不存在"，记入异常清单 |
| `Authentication failed` | 认证失败 | 检查凭证是否正确，备注"认证失败" |
| `Could not resolve host` | 无法解析域名 | 备注"仓库地址无法访问" |
| `Connection refused` | 连接被拒绝 | 备注"仓库服务器拒绝连接" |
| `does not appear to be a git repository` | 非 Git 仓库 | 备注"地址不是有效的 Git 仓库" |
| `empty repository` | 仓库为空 | 备注"仓库为空，无代码提交" |

### 超时处理

设置 Git 超时，避免单个学生阻塞整体流程：

```bash
# 设置 30 秒超时
timeout 30 git clone --depth 1 "$REPO_URL" "$TARGET_DIR" 2>&1
if [ $? -eq 124 ]; then
    echo "克隆超时（超过 30 秒）"
fi
```

---

## 四、批量优化建议

### 浅克隆

使用 `--depth 1` 只获取最新版本，大幅减少下载量：

```bash
git clone --depth 1 https://...
```

### 并发控制

当学生数量较多（50+）时，可分批处理，每批 5-10 人。

### 常见检查命令速查

```bash
# 查看提交日志
cd "$STUDENT_DIR"
git log --oneline -5

# 查看文件变更量
git log --stat --oneline | head -20

# 查看代码行数统计
find . -name "*.java" -not -path "./.git/*" | xargs wc -l 2>/dev/null | tail -1

# 搜索特定字符串
grep -r "关键字" --include="*.java" --include="*.py" --include="*.js" . | head -20
```
