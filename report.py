"""
生成检查报告
"""
from pathlib import Path


def get_soda_version():
    """获取 Soda Core 版本号"""
    try:
        import pkg_resources
        return pkg_resources.get_distribution("soda-core-duckdb").version
    except:
        return "3.0.x"


def save_reports(all_results):
    """保存报告，Soda Core 官方格式"""
    if not all_results:
        return

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    soda_version = get_soda_version()

    for name, results in all_results.items():
        checks = results.get('checks', [])

        total = len(checks)
        passed = sum(1 for c in checks if c.get('outcome') == 'pass')
        failed = sum(1 for c in checks if c.get('outcome') == 'fail')
        warnings = sum(1 for c in checks if c.get('outcome') == 'warn')
        errors = sum(1 for c in checks if c.get('outcome') == 'error')

        lines = []
        lines.append(f"Soda Core {soda_version}")
        lines.append("Scan summary:")
        lines.append(f"{passed}/{total} checks PASSED: ")
        lines.append("")

        for check in checks:
            check_name = check.get('name', 'unnamed')
            outcome = check.get('outcome', 'unknown')
            if outcome == 'pass':
                status = "✅"
            elif outcome == 'fail':
                status = "❌"
            elif outcome == 'warn':
                status = "⚠️"
            else:
                status = "❗"
            lines.append(f"  {status} {check_name} [{outcome.upper()}]")

            # 输出展示数据
            show_data = check.get('show_on_fail_data')
            if show_data:
                lines.append("     📋 详情:")
                for row in show_data:
                    lines.append(f"        {row}")

        lines.append("")
        if failed == 0 and errors == 0:
            lines.append("All is good. No failures. No warnings. No errors.")
        else:
            details = []
            if failed > 0:
                details.append(f"{failed} failures")
            if warnings > 0:
                details.append(f"{warnings} warnings")
            if errors > 0:
                details.append(f"{errors} errors")
            lines.append(f"Oops! {', '.join(details)}.")

        report_path = reports_dir / f"{name}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"📄 报告已保存: {report_path}")