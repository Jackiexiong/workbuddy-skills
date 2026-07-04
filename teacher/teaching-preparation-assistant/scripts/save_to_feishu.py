#!/usr/bin/env python3
"""
save_to_feishu.py — 将 Markdown 文件导入飞书云文档

一次性配置（只需做一次）：
  python save_to_feishu.py --init     # 从模板创建配置文件，然后手动填入凭据
  python save_to_feishu.py --check    # 验证配置是否正确

日常使用（配置完成后）：
  python save_to_feishu.py --file "文档.md" --name "文档标题"

配置说明详见 references/feishu-integration.md
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import uuid

FEISHU_BASE = "https://open.feishu.cn/open-apis"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "feishu_config.json")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "feishu_config_template.json")


# ============================================================
#  配置管理
# ============================================================

def find_config():
    """查找配置文件，返回 (路径, 配置字典) 或 (None, None)"""
    # 1. 命令行 --config 指定的路径
    env_config = os.environ.get("FEISHU_CONFIG_PATH", "")
    if env_config and os.path.exists(env_config):
        return env_config, _load_json(env_config)

    # 2. 脚本同目录下的 feishu_config.json
    if os.path.exists(CONFIG_PATH):
        return CONFIG_PATH, _load_json(CONFIG_PATH)

    # 3. 用户主目录下的 .feishu_config.json
    home_config = os.path.join(os.path.expanduser("~"), ".feishu_config.json")
    if os.path.exists(home_config):
        return home_config, _load_json(home_config)

    return None, None


def _load_json(path):
    """加载 JSON 文件，过滤掉以 _ 开头的注释字段"""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # 过滤掉 _ 开头的注释字段
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def load_config(config_override=""):
    """加载配置，优先级：环境变量 > 配置文件"""
    # 如果命令行指定了配置路径
    if config_override:
        if not os.path.exists(config_override):
            print(f"错误：指定的配置文件不存在: {config_override}")
            sys.exit(1)
        os.environ["FEISHU_CONFIG_PATH"] = config_override

    # 检查环境变量方式
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if app_id and app_secret:
        return {"app_id": app_id, "app_secret": app_secret, "folder_token": ""}

    # 检查配置文件
    path, config = find_config()
    if config is not None:
        return config

    # 未找到配置
    print("=" * 60)
    print("错误：未找到飞书配置")
    print("=" * 60)
    print()
    print("请先运行以下命令进行一次性配置：")
    print()
    print("  python save_to_feishu.py --init")
    print()
    print("这会从模板创建配置文件，你只需填入飞书应用凭据即可。")
    print("详细配置指南请参考 references/feishu-integration.md")
    sys.exit(1)


# ============================================================
#  初始化与验证
# ============================================================

def cmd_init():
    """从模板创建配置文件"""
    if os.path.exists(CONFIG_PATH):
        print(f"配置文件已存在: {CONFIG_PATH}")
        answer = input("是否覆盖？(y/n): ").strip().lower()
        if answer != "y":
            print("已取消")
            return

    if not os.path.exists(TEMPLATE_PATH):
        print(f"错误：模板文件不存在: {TEMPLATE_PATH}")
        sys.exit(1)

    # 读取模板并写入配置文件
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("=" * 60)
    print("配置文件已创建!")
    print("=" * 60)
    print()
    print(f"  路径: {CONFIG_PATH}")
    print()
    print("接下来请打开此文件，填入你的飞书应用凭据：")
    print()
    print("  1. app_id      — 填入飞书应用的 App ID")
    print("  2. app_secret  — 填入飞书应用的 App Secret")
    print("  3. folder_token — 填入飞书文件夹的 token（可选）")
    print()
    print("填好后运行以下命令验证配置是否正确：")
    print()
    print("  python save_to_feishu.py --check")
    print()
    print("如何获取飞书应用凭据？请参考 references/feishu-integration.md")


def cmd_check(config_override=""):
    """验证配置是否正确"""
    print("飞书配置验证")
    print("=" * 60)
    print()

    # Step 1: 检查配置文件是否存在
    path, config = find_config()
    if config is None and not config_override:
        print("[FAIL] 未找到配置文件")
        print()
        print("请先运行: python save_to_feishu.py --init")
        sys.exit(1)

    if config_override:
        if not os.path.exists(config_override):
            print(f"[FAIL] 指定的配置文件不存在: {config_override}")
            sys.exit(1)
        os.environ["FEISHU_CONFIG_PATH"] = config_override
        path, config = find_config()

    print(f"[OK] 配置文件路径: {path}")
    print()

    # Step 2: 检查必填字段
    app_id = config.get("app_id", "")
    app_secret = config.get("app_secret", "")
    folder_token = config.get("folder_token", "")

    if not app_id or app_id.startswith("在此填入"):
        print("[FAIL] app_id 未配置（还是模板默认值）")
        sys.exit(1)
    print(f"[OK] app_id: {app_id[:8]}...")

    if not app_secret or app_secret.startswith("在此填入"):
        print("[FAIL] app_secret 未配置（还是模板默认值）")
        sys.exit(1)
    print(f"[OK] app_secret: {'*' * 8}...（已设置）")

    if folder_token:
        print(f"[OK] folder_token: {folder_token}")
    else:
        print(f"[INFO] folder_token 未设置（文档将保存到应用默认空间）")

    print()

    # Step 3: 尝试获取 token
    print("正在验证飞书 API 连接...")
    try:
        token = get_tenant_access_token(app_id, app_secret)
        print()
        print("=" * 60)
        print("配置验证通过! 可以正常使用飞书导入功能了。")
        print("=" * 60)
        print()
        print("使用方法：")
        print('  python save_to_feishu.py --file "文档.md" --name "文档标题"')
    except Exception as e:
        print()
        print(f"[FAIL] API 验证失败: {e}")
        print()
        print("可能的原因：")
        print("  1. app_id 或 app_secret 不正确")
        print("  2. 应用尚未发布（需在开发者后台点击「创建版本」并「发布」）")
        print("  3. 应用权限未开通（需开通 drive:drive, drive:file:upload, docx:document）")
        sys.exit(1)


# ============================================================
#  飞书 API 调用
# ============================================================

def get_tenant_access_token(app_id, app_secret):
    """获取 tenant_access_token"""
    url = f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if result.get("code") != 0:
        raise Exception(f"获取 token 失败: {result.get('msg')}")

    token = result.get("tenant_access_token")
    print(f"[OK] 获取 tenant_access_token 成功")
    return token


def upload_file(token, file_path, file_name):
    """上传文件到飞书云空间，返回 file_token"""
    url = f"{FEISHU_BASE}/drive/v1/files/upload_all"
    file_size = os.path.getsize(file_path)

    # 构建 multipart/form-data
    boundary = uuid.uuid4().hex
    body = bytearray()

    # file_name 字段
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="file_name"\r\n\r\n')
    body.extend(f"{file_name}\r\n".encode())

    # parent_type 字段
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="parent_type"\r\n\r\n')
    body.extend(b"ccm_import_open\r\n")

    # size 字段
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="size"\r\n\r\n')
    body.extend(f"{file_size}\r\n".encode())

    # file 字段
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode()
    )
    body.extend(b"Content-Type: text/markdown\r\n\r\n")

    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if result.get("code") != 0:
        raise Exception(f"上传文件失败: {result.get('msg')}")

    file_token = result["data"]["file_token"]
    print(f"[OK] 文件上传成功, file_token: {file_token}")
    return file_token


def create_import_task(token, file_token, doc_name, folder_token=""):
    """创建导入任务，将上传的 md 文件导入为飞书文档"""
    url = f"{FEISHU_BASE}/drive/v1/import_tasks"

    payload = {
        "file_extension": "md",
        "file_token": file_token,
        "type": "docx",
        "name": doc_name,
        "point": {
            "mount_type": "1"
        }
    }

    # 如果指定了文件夹 token，添加到 point 中
    if folder_token:
        payload["point"]["mount_key"] = folder_token

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if result.get("code") != 0:
        raise Exception(f"创建导入任务失败: {result.get('msg')}")

    ticket = result["data"]["ticket"]
    print(f"[OK] 导入任务已创建, ticket: {ticket}")
    return ticket


def poll_import_result(token, ticket, max_retries=30, interval=2):
    """轮询导入任务结果"""
    url = f"{FEISHU_BASE}/drive/v1/import_tasks/{ticket}"

    for i in range(max_retries):
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("code") != 0:
            raise Exception(f"查询导入结果失败: {result.get('msg')}")

        job_status = result["data"]["result"]["job_status"]

        if job_status == 1:
            # 导入成功
            doc_url = result["data"]["result"].get("url", "")
            doc_token = result["data"]["result"].get("token", "")
            print(f"[OK] 导入成功!")
            print(f"     文档链接: {doc_url}")
            return {"url": doc_url, "token": doc_token}
        elif job_status == 2:
            error_msg = result["data"]["result"].get("job_error_msg", "未知错误")
            raise Exception(f"导入失败: {error_msg}")

        # 仍在处理中，等待后重试
        print(f"  [{i+1}/{max_retries}] 导入处理中... 等待 {interval} 秒")
        time.sleep(interval)

    raise Exception(f"导入超时，已等待 {max_retries * interval} 秒")


# ============================================================
#  主流程
# ============================================================

def cmd_upload(args):
    """执行文档导入"""
    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误：文件不存在: {args.file}")
        sys.exit(1)

    # 加载配置
    config = load_config(args.config)

    app_id = config.get("app_id", "")
    app_secret = config.get("app_secret", "")
    folder_token = args.folder or config.get("folder_token", "")

    if not app_id or not app_secret:
        print("错误：配置中缺少 app_id 或 app_secret")
        print("请运行: python save_to_feishu.py --init")
        sys.exit(1)

    file_path = os.path.abspath(args.file)
    file_name = os.path.basename(file_path)

    print(f"飞书云文档导入工具")
    print(f"  文件: {file_path}")
    print(f"  标题: {args.name}")
    if folder_token:
        print(f"  文件夹: {folder_token}")
    print()

    # Step 0: 获取 token
    token = get_tenant_access_token(app_id, app_secret)

    # Step 1: 上传文件
    file_token = upload_file(token, file_path, file_name)

    # Step 2: 创建导入任务
    ticket = create_import_task(token, file_token, args.name, folder_token)

    # Step 3: 轮询结果
    result = poll_import_result(token, ticket)

    print()
    print("=" * 60)
    print(f"飞书文档创建成功!")
    print(f"  标题: {args.name}")
    print(f"  链接: {result['url']}")
    print("=" * 60)

    # 将结果写入 JSON 文件，方便其他程序读取
    result_file = os.path.splitext(file_path)[0] + "_feishu_result.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({"name": args.name, "url": result["url"], "token": result["token"]}, f,
                  ensure_ascii=False, indent=2)
    print(f"  结果已保存: {result_file}")


def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 文件导入飞书云文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
一次性配置（只需做一次）：
  python save_to_feishu.py --init       # 创建配置文件
  python save_to_feishu.py --check      # 验证配置

日常使用：
  python save_to_feishu.py --file "文档.md" --name "文档标题"

配置说明详见 references/feishu-integration.md
        """
    )
    parser.add_argument("--file", help="Markdown 文件路径")
    parser.add_argument("--name", help="飞书文档标题")
    parser.add_argument("--folder", default="", help="飞书文件夹 token（覆盖配置文件中的设置）")
    parser.add_argument("--config", default="", help="配置文件路径（可选）")
    parser.add_argument("--init", action="store_true", help="从模板创建配置文件")
    parser.add_argument("--check", action="store_true", help="验证配置是否正确")
    args = parser.parse_args()

    if args.init:
        cmd_init()
        return

    if args.check:
        cmd_check(args.config)
        return

    if not args.file or not args.name:
        parser.print_help()
        sys.exit(1)

    cmd_upload(args)


if __name__ == "__main__":
    main()
