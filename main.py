"""
主入口
"""
import sys
import os
from run_checks import run_checks
from report import save_reports


def get_base_dir():
    """获取基础目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


# 设置控制台输出编码，替换 emoji 为纯文本
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

    # 替换全局 print 中的 emoji
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
OUTPUT_DIR = get_base_dir()

DRILL_HOST = "localhost"
DRILL_PORT = 8047
SOURCES = [
    "mysql.data_source_his",
    "mysql.standard_interface",
    "mongo.test"
]

if __name__ == '__main__':
    print(f"[*] 工作目录: {BASE_DIR}")
    print(f"[*] 输出目录: {OUTPUT_DIR}")

    results = run_checks(
        drill_host=DRILL_HOST,
        drill_port=DRILL_PORT,
        sources=SOURCES,
        base_dir=BASE_DIR
    )

    if results:
        save_reports(results, base_dir=OUTPUT_DIR)

    input("\n按 Enter 键退出...")