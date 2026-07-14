"""
从 Drill 服务获取数据源
"""
import requests
import pandas as pd


def query_drill(sql, host="localhost", port=8047):
    """通过 REST API 查询 Drill"""
    try:
        response = requests.post(
            f"http://{host}:{port}/query.json",
            json={"queryType": "SQL", "query": sql},
            timeout=300
        )
        data = response.json()

        columns = data.get("columns", [])
        rows = data.get("rows", [])

        if not columns or not rows:
            return pd.DataFrame()

        col_names = [col for col in columns]
        df = pd.DataFrame(rows, columns=col_names)

        return df
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return pd.DataFrame()


def get_tables(source_path, host, port):
    """获取指定路径下的所有表"""
    sql = f"SHOW TABLES IN {source_path}"
    df = query_drill(sql, host, port)

    if df.empty:
        return []

    return df["TABLE_NAME"].tolist()


def load_data_from_drill(sources, host="localhost", port=8047):
    """从 Drill 加载数据"""

    dataframes = {}
    total = 0
    total_skipped = 0

    for source in sources:
        tables = get_tables(source, host, port)

        if not tables:
            print(f"📁 {source}: 0 个表")
            continue

        source_total = 0
        source_skipped = 0

        for table_name in tables:
            try:
                sql = f"SELECT * FROM {source}.{table_name}"
                df = query_drill(sql, host, port)

                if df.empty:
                    source_skipped += 1
                    continue

                dataframes[table_name] = df
                source_total += 1

            except Exception:
                source_skipped += 1

        print(f"📁 {source}: {source_total} 个表", end="")
        if source_skipped > 0:
            print(f" (跳过 {source_skipped} 个)")
        else:
            print()

        total += source_total
        total_skipped += source_skipped

    print(f"\n✅ 从 Drill 加载完成 ({total} 个表)")
    if total_skipped > 0:
        print(f"⚠️  跳过 {total_skipped} 个空表")

    return dataframes