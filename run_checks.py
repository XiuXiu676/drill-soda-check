"""
执行 Soda 检查
"""
from pathlib import Path
from soda.scan import Scan
from data_source import load_data_from_drill
import duckdb


def parse_show_on_fail_queries(check_file):
    """按行解析 yml 文件，提取所有 show_on_fail 查询"""
    result = {}
    try:
        with open(check_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            if '# show_on_fail:' in stripped:
                sql_lines = []
                after_marker = stripped.split('# show_on_fail:', 1)[1].strip()
                if after_marker and after_marker != '|':
                    sql_lines.append(after_marker)

                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('#') and 'name:' not in lines[j]:
                    sql_part = lines[j].strip().lstrip('#').strip()
                    if sql_part and sql_part != '|':
                        sql_lines.append(sql_part)
                    j += 1

                check_name = None
                k = j
                while k < len(lines):
                    line_k = lines[k].strip()
                    if line_k.startswith('name:') and not lines[k].startswith('- name:'):
                        check_name = lines[k].split('name:', 1)[1].strip().strip('"').strip("'")
                        break
                    if line_k.startswith('- ') and k > j:
                        break
                    k += 1

                if check_name and sql_lines:
                    sql = ' '.join(sql_lines).strip()
                    result[check_name] = sql

                i = j
            else:
                i += 1

    except Exception as e:
        print(f"⚠️  解析 show_on_fail 失败: {e}")

    return result


def show_data(conn, sql, limit=10):
    """执行展示查询并打印结果，返回数据"""
    if not sql:
        return None
    try:
        rows = conn.execute(sql).fetchmany(limit)
        if rows:
            print(f"   📋 详情:")
            for row in rows:
                print(f"      {row}")
        return rows
    except Exception as e:
        print(f"   ⚠️  展示查询失败: {e}")
        return None


def run_checks(drill_host="localhost", drill_port=8047, sources=None, base_dir="."):
    """执行检查，返回结果"""
    if sources is None:
        sources = []

    checks_dir = Path(base_dir) / "checks"

    if not checks_dir.exists():
        print("❌ checks 目录不存在")
        return None

    check_files = list(checks_dir.glob("*.yml"))

    if not check_files:
        print("❌ 未找到检查文件")
        return None

    dataframes = load_data_from_drill(sources, drill_host, drill_port)

    if not dataframes:
        print("❌ 没有加载到数据")
        return None

    conn = duckdb.connect(':memory:')
    for table_name, df in dataframes.items():
        conn.register(table_name, df)

    all_results = {}

    for check_file in check_files:
        show_queries = parse_show_on_fail_queries(str(check_file))
        if show_queries:
            print(f"📋 {check_file.stem}: 已加载 {len(show_queries)} 个展示查询")

        scan = Scan()
        scan.set_data_source_name("local_json")
        scan.add_duckdb_connection(conn, data_source_name="local_json")
        scan.add_sodacl_yaml_file(str(check_file))
        scan.set_scan_definition_name(check_file.stem)

        try:
            scan.execute()
            results = scan.get_scan_results()
            all_results[check_file.stem] = results

            for check in results.get('checks', []):
                name = check.get('name', '未知检查')
                outcome = check.get('outcome', 'unknown')
                status = "✅" if outcome == 'pass' else "❌"
                print(f"{status} {name}")

                if outcome == 'fail' and name in show_queries:
                    data = show_data(conn, show_queries[name])
                    if data:
                        check['show_on_fail_data'] = [str(row) for row in data]

        except Exception as e:
            print(f"❌ 执行失败: {e}")

    conn.close()

    return all_results