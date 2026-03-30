"""
PhoneOSINT - Report Generator Module
Generates formatted reports in Console, JSON, and HTML formats.
"""

import json
import os
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = "reports"


class ReportGenerator:
    """Generate formatted OSINT reports."""

    SECTION_EMOJIS = {
        "phone_info": "📞",
        "truecaller": "🔍",
        "whatsapp": "💬",
        "telegram": "✈️",
        "facebook": "👤",
        "instagram": "📸",
        "google_dorks": "🔎",
        "social_scan": "🔗",
    }

    def __init__(self, phone_number: str, results: dict):
        self.phone_number = phone_number
        self.results = results
        self.console = Console()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_report(self):
        """Print formatted report to console."""
        self.console.print(
            Panel(
                f"📱 Phone OSINT Report for: {self.phone_number}\n"
                f"📅 Generated: {self.timestamp}",
                title="[bold]PHONE OSINT REPORT[/bold]",
                style="bold cyan",
            )
        )

        for section_name in [
            "phone_info", "truecaller", "whatsapp",
            "telegram", "facebook", "instagram",
        ]:
            if section_name in self.results:
                emoji = self.SECTION_EMOJIS.get(section_name, "📋")
                title = section_name.replace("_", " ").title()
                self._print_section(
                    f"{emoji} {title}",
                    self.results[section_name],
                )

        # Social scan — special table
        if "social_scan" in self.results:
            self._print_social_scan(self.results["social_scan"])

        # Google dorks — special table
        if "google_dorks" in self.results:
            self._print_dorks(self.results["google_dorks"])

    def _print_section(self, title: str, data: dict):
        """Print a single section as a Rich table."""
        if not isinstance(data, dict):
            return

        table = Table(title=title, show_lines=True)
        table.add_column("Property", style="cyan", width=22)
        table.add_column("Value", style="green")

        for key, value in data.items():
            if key in ("raw_response", "numverify") or key.startswith("_"):
                continue

            if isinstance(value, dict):
                for k, v in value.items():
                    table.add_row(f"  {key}.{k}", str(v))
            elif isinstance(value, list):
                if value:
                    table.add_row(
                        str(key),
                        ", ".join(str(v) for v in value[:5]),
                    )
            elif value is True:
                table.add_row(str(key), "[green]✓ Yes[/green]")
            elif value is False:
                table.add_row(str(key), "[red]✗ No[/red]")
            elif value is None:
                table.add_row(str(key), "[yellow]Unknown[/yellow]")
            elif value == "":
                continue
            else:
                table.add_row(str(key), str(value))

        self.console.print(table)

    def _print_social_scan(self, data: dict):
        """Print social scan results as a compact table."""
        table = Table(title="🔗 Additional Platforms", show_lines=True)
        table.add_column("Platform", style="cyan", width=18)
        table.add_column("Status", style="white", width=12)
        table.add_column("Link / Note", style="blue")

        for platform, info in data.items():
            if not isinstance(info, dict):
                continue

            exists = info.get("exists")
            if exists is True:
                status = "[green]✓ Found[/green]"
            elif exists is False:
                status = "[red]✗ Not Found[/red]"
            else:
                status = "[yellow]? Unknown[/yellow]"

            link = (
                info.get("search_url")
                or info.get("deep_link")
                or info.get("note", "")
            )

            # Truncate long URLs
            if isinstance(link, str) and len(link) > 60:
                link = link[:57] + "..."

            table.add_row(platform.title(), status, str(link))

        self.console.print(table)

    def _print_dorks(self, data: dict):
        """Print Google dork search URLs."""
        dorks = data.get("social_media_dorks", {})
        if not dorks:
            return

        table = Table(
            title="🔎 Google Dork Search URLs", show_lines=True
        )
        table.add_column("Platform", style="cyan", width=18)
        table.add_column("Search URL", style="blue")

        for platform, info in dorks.items():
            url = info.get("search_url", "N/A")
            table.add_row(platform.title(), url)

        self.console.print(table)

    def save_json(self, output_dir: str = None) -> str:
        """Save results as JSON file."""
        output_dir = output_dir or OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        clean_number = (
            self.phone_number.replace("+", "").replace(" ", "")
        )
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            output_dir, f"report_{clean_number}_{ts}.json"
        )

        report = {
            "phone_number": self.phone_number,
            "timestamp": self.timestamp,
            "results": self._clean_results(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        self.console.print(
            f"\n[green]💾 JSON Report saved: {filename}[/green]"
        )
        return filename

    def save_html(self, output_dir: str = None) -> str:
        """Save results as HTML file."""
        output_dir = output_dir or OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        clean_number = (
            self.phone_number.replace("+", "").replace(" ", "")
        )
        filename = os.path.join(
            output_dir, f"report_{clean_number}.html"
        )

        html = self._generate_html()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        self.console.print(
            f"[green]💾 HTML Report saved: {filename}[/green]"
        )
        return filename

    def _clean_results(self) -> dict:
        """Remove raw/internal data for clean JSON output."""
        cleaned = {}
        for section, data in self.results.items():
            if isinstance(data, dict):
                cleaned[section] = {
                    k: v
                    for k, v in data.items()
                    if k not in ("raw_response",)
                }
            else:
                cleaned[section] = data
        return cleaned

    def _generate_html(self) -> str:
        """Generate complete HTML report."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhoneOSINT Report - {self.phone_number}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 30px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #00d4ff;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header p {{ color: #aaa; font-size: 1.1em; }}
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .section h2 {{
            background: rgba(0, 212, 255, 0.15);
            color: #00d4ff;
            padding: 15px 20px;
            font-size: 1.2em;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{
            padding: 12px 20px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        th {{ color: #00d4ff; width: 200px; font-weight: 600; }}
        td {{ color: #e0e0e0; word-break: break-all; }}
        .found {{ color: #00ff88; font-weight: bold; }}
        .not-found {{ color: #ff4444; }}
        .unknown {{ color: #ffa500; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .profile-pic {{
            width: 80px; height: 80px; border-radius: 50%;
            border: 2px solid #00d4ff; margin: 5px 0;
        }}
        .footer {{
            text-align: center; padding: 20px; color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 30px;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📱 PhoneOSINT Report</h1>
        <p><strong>Target:</strong> {self.phone_number}</p>
        <p><strong>Generated:</strong> {self.timestamp}</p>
    </div>
"""

        for section, data in self.results.items():
            if not isinstance(data, dict):
                continue

            emoji = self.SECTION_EMOJIS.get(section, "📋")
            section_title = section.replace("_", " ").title()

            html += f"""
    <div class="section">
        <h2>{emoji} {section_title}</h2>
        <table>
"""
            for key, value in data.items():
                if key in ("raw_response",):
                    continue

                if isinstance(value, dict):
                    for k, v in value.items():
                        v_html = self._format_html_value(v)
                        html += (
                            f"            <tr>"
                            f"<th>{key}.{k}</th>"
                            f"<td>{v_html}</td>"
                            f"</tr>\n"
                        )
                elif isinstance(value, list):
                    if value:
                        v_str = ", ".join(
                            str(v) for v in value[:10]
                        )
                        html += (
                            f"            <tr>"
                            f"<th>{key}</th>"
                            f"<td>{v_str}</td>"
                            f"</tr>\n"
                        )
                elif value == "" or value is None:
                    continue
                else:
                    v_html = self._format_html_value(value)
                    html += (
                        f"            <tr>"
                        f"<th>{key}</th>"
                        f"<td>{v_html}</td>"
                        f"</tr>\n"
                    )

            html += """        </table>
    </div>
"""

        html += f"""
    <div class="footer">
        <p>Generated by PhoneOSINT | {self.timestamp}</p>
        <p>⚠️ For authorized and educational use only</p>
    </div>
</div>
</body>
</html>"""

        return html

    def _format_html_value(self, value) -> str:
        """Format a value for HTML display."""
        if value is True:
            return '<span class="found">✓ Yes</span>'
        elif value is False:
            return '<span class="not-found">✗ No</span>'
        elif value is None:
            return '<span class="unknown">Unknown</span>'
        elif isinstance(value, str) and value.startswith("http"):
            exts = [".jpg", ".jpeg", ".png", ".gif"]
            if any(ext in value.lower() for ext in exts):
                return (
                    f'<a href="{value}" target="_blank">'
                    f'<img src="{value}" class="profile-pic" '
                    f'alt="Profile"></a>'
                )
            return f'<a href="{value}" target="_blank">{value}</a>'
        else:
            return str(value)