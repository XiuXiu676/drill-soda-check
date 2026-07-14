"""
读取 data 目录下的 JSON 文件
"""
from pathlib import Path
import pandas as pd


def load_all_data(data_dir: str = "data"):
    """加载所有 JSON 文件为 DataFrame 字典"""
    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"❌ 目录不存在: {data_dir}")
        return {}

    sources = ["data_source_his", "standard_interface", "data_api_ods"]

    dataframes = {}
    total_files = 0
    skipped_files = 0

    for source_name in sources:
        source_path = data_path / source_name

        if not source_path.exists():
            continue

        json_files = sorted(source_path.glob("*.json"))

        for json_file in json_files:
            table_name = json_file.stem

            try:
                df = pd.read_json(json_file)

                # 跳过空 DataFrame
                if df.empty or len(df.columns) == 0:
                    skipped_files += 1
                    continue

                dataframes[table_name] = df
                total_files += 1

            except Exception as e:
                skipped_files += 1
                print(f"⚠️  {json_file.name}: {e}")

    print(f"✅ 加载完成 ({total_files} 个表")
    if skipped_files > 0:
        print(f"⚠️  跳过 {skipped_files} 个空文件/错误文件)")

    return dataframes