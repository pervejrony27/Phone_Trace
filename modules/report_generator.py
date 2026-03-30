def generate_report(data, out_path="reports/report.txt"):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(data))
    return out_path
