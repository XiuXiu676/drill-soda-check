"""
主入口
"""
import sys
import os
import json
from run_checks import run_checks
from report import save_reports


def get_base_dir():
    """获取基础目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    """从 exe 同级目录加载配置文件"""
    config_path = os.path.join(get_base_dir(), 'config.json')

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"[WARN] 未找到配置文件: {config_path}")
        print("[WARN] 使用默认配置")
        return {
            "drill_host": "localhost",
            "drill_port": 8047,
            "sources": [
                "mysql.data_source_his",
                "mysql.standard_interface",
                "mongo.test"
            ]
        }


# 设置控制台输出编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

    import builtins
    _original_print = builtins.print

    def safe_print(*args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                arg = arg.replace('✅', '[PASS]')
                arg = arg.replace('❌', '[FAIL]')
                arg = arg.replace('⚠️', '[WARN]')
                arg = arg.replace('📁', '>>>')
                arg = arg.replace('📋', '[INFO]')
                arg = arg.replace('📄', '[SAVE]')
            new_args.append(arg)
        _original_print(*new_args, **kwargs)

    builtins.print = safe_print


BASE_DIR = get_base_dir()
config = load_config()

DRILL_HOST = config.get("drill_host", "localhost")
DRILL_PORT = config.get("drill_port", 8047)
SOURCES = config.get("sources", [])

if __name__ == '__main__':
    print(f"[*] 工作目录: {BASE_DIR}")
    print(f"[*] Drill: {DRILL_HOST}:{DRILL_PORT}")
    print(f"[*] 数据源: {SOURCES}")

    results = run_checks(
        drill_host=DRILL_HOST,
        drill_port=DRILL_PORT,
        sources=SOURCES,
        base_dir=BASE_DIR
    )

    if results:
        save_reports(results, base_dir=BASE_DIR)

    input("\n按 Enter 键退出...")