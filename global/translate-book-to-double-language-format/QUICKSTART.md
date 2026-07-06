# 快速开始指南

## 🚀 5 分钟快速上手

### 第 1 步：安装（仅需一次）

#### Windows 用户：
双击运行：`install_skill.bat`

#### macOS/Linux 用户：
```bash
chmod +x install_skill.sh
./install_skill.sh
```

或者手动安装依赖：
```bash
pip install pypandoc beautifulsoup4 markdown
```

然后安装：
- **Calibre**（必须）：https://calibre-ebook.com/download
- **Pandoc**（推荐）：https://pandoc.org/installing.html

### 第 2 步：验证安装

运行环境检查：
```bash
python check_env.py
```

确保所有检查都显示 **✓ PASSED**

### 第 3 步：开始翻译！

在 WorkBuddy 中只需要说：

```
帮我把这本书翻译成中文双语对照版：D:\Books\我的书.epub
```

或者更详细的：
```
请翻译这本书：D:\Books\小说.pdf
目标语言：中文
输出格式：保持原格式
```

---

## 📋 支持的格式

| 输入格式 | 输出格式 |
|---------|---------|
| EPUB | EPUB ✓ |
| PDF | PDF ✓ |
| DOCX | DOCX ✓ |

输出文件会自动添加 `-英中双语` 后缀。

---

## 🎯 功能特性

✅ **双语对照** - 原文 + 译文逐段显示  
✅ **保持格式** - 输出与输入相同格式  
✅ **智能分块** - 大文件自动拆分，断点续传  
✅ **术语一致** - 自动构建术语表  
✅ **并行翻译** - 多块同时翻译更高效  

---

## 🔧 故障排除

### 问题：提示 Calibre 未找到
**解决方法**：
1. 从 https://calibre-ebook.com/download 下载并安装 Calibre
2. Windows：安装后重启终端，或手动添加到 PATH
3. 再次运行 `check_env.py` 验证

### 问题：翻译中途停止
**解决方法**：
- 重新运行翻译命令，支持断点续译
- 已翻译的部分会跳过，只翻译未完成的

### 问题：生成的 EPUB 打开乱码
**解决方法**：
- 确认源文件编码正确
- 检查 Calibre 安装完整

---

## 📁 输出文件说明

翻译完成后，你会得到：
- `原文件名-英中双语.epub` - 最终双语图书 ✓
- `原文件名_temp/` - 临时工作目录（可删除）

---

## 💡 使用技巧

1. **先测试小文件** - 先用小书测试流程是否正常
2. **检查术语表** - 翻译前可查看和编辑 `glossary.json`
3. **保持网络** - 翻译需要网络连接（AI 服务）

---

## 📞 需要帮助？

查看完整文档：`README.md`  
或运行环境检查：`python check_env.py`

---

祝你使用愉快！🎉

