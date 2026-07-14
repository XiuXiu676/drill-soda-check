"""
主入口
"""
from run_checks import run_checks
from report import save_reports

# 数据源配置
DRILL_HOST = "localhost"
DRILL_PORT = 8047
SOURCES = [
    "mysql.data_source_his",
    "mysql.standard_interface",
    "mongo.test"
]

if __name__ == '__main__':
    results = run_checks(
        drill_host=DRILL_HOST,
        drill_port=DRILL_PORT,
        sources=SOURCES
    )

    if results:
        save_reports(results)