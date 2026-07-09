#!/usr/bin/env python3
"""
Fetch latest NAV/dividend data from cnyes.com and SPY prices from Yahoo Finance,
then update the fund simulator HTML files.

Runs monthly via GitHub Actions (.github/workflows/update-fund-data.yml).
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone

import requests

CNYES_DIVIDEND_URL = "https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/dividend"
FUNDS = {
    "AM":   "B20,073",
    "AMG7": "B2abw8B",
}
HTML_FILES = ["fund-simulator.html", "安聯收益成長基金投資模擬器.html"]


def fetch_all_dividends(fund_id):
    """Fetch all dividend history pages from cnyes API."""
    all_records = []
    page = 1
    while True:
        resp = requests.get(
            CNYES_DIVIDEND_URL.format(fund_id=fund_id),
            params={"page": page, "limit": 200},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()["items"]
        records = data["data"]
        if not records:
            break
        all_records.extend(records)
        if page >= data["last_page"]:
            break
        page += 1
    return all_records


def dividends_to_js_array(records):
    """Convert cnyes dividend records to the JS data format used in HTML."""
    entries = []
    for r in records:
        ts = r["excludingDate"]
        dt = datetime.fromtimestamp(ts, tz=timezone.utc) + timedelta(days=1)
        date_str = dt.strftime("%Y-%m-%d")
        nav = round(float(r["nav"]), 4)
        dividend = round(float(r["totalDistribution"]), 5)
        yld = round(float(r["distributionYield"]), 5)
        entries.append({"date": date_str, "nav": nav, "dividend": dividend, "yield": yld})
    entries.sort(key=lambda x: x["date"])
    return entries


def fetch_spy_monthly():
    """Fetch SPY monthly adjusted close prices using yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        print("yfinance not installed, trying pip install...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q"])
        import yfinance as yf

    spy = yf.Ticker("SPY")
    hist = spy.history(period="max", interval="1mo")
    entries = []
    for idx, row in hist.iterrows():
        date_str = idx.strftime("%Y-%m-01")
        entries.append({"date": date_str, "close": round(float(row["Close"]), 2)})
    entries.sort(key=lambda x: x["date"])
    # Keep only from 2012-01 onward (matching original data)
    entries = [e for e in entries if e["date"] >= "2012-01-01"]
    return entries


def format_js_array(entries):
    """Format entries as compact JSON matching the original HTML style."""
    return json.dumps(entries, separators=(",", ":"), ensure_ascii=False)


def update_html(filepath, am_data, amg7_data, spy_data):
    """Replace the data arrays in the HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    am_js = format_js_array(am_data)
    amg7_js = format_js_array(amg7_data)
    spy_js = format_js_array(spy_data)

    content = re.sub(
        r"const AM_DATA = \[.*?\];",
        f"const AM_DATA = {am_js};",
        content,
        count=1,
    )
    content = re.sub(
        r"const AMG7_DATA = \[.*?\];",
        f"const AMG7_DATA = {amg7_js};",
        content,
        count=1,
    )
    content = re.sub(
        r"const SPY_DATA = \[.*?\];",
        f"const SPY_DATA = {spy_js};",
        content,
        count=1,
    )

    if content == original:
        print(f"  {filepath}: no changes")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  {filepath}: updated")
    return True


def main():
    print("Fetching AM dividend data...")
    am_raw = fetch_all_dividends(FUNDS["AM"])
    am_data = dividends_to_js_array(am_raw)
    print(f"  AM: {len(am_data)} records (latest: {am_data[-1]['date'] if am_data else 'N/A'})")

    print("Fetching AMg7 dividend data...")
    amg7_raw = fetch_all_dividends(FUNDS["AMG7"])
    amg7_data = dividends_to_js_array(amg7_raw)
    print(f"  AMg7: {len(amg7_data)} records (latest: {amg7_data[-1]['date'] if amg7_data else 'N/A'})")

    print("Fetching SPY monthly data...")
    spy_data = fetch_spy_monthly()
    print(f"  SPY: {len(spy_data)} records (latest: {spy_data[-1]['date'] if spy_data else 'N/A'})")

    print("Updating HTML files...")
    changed = False
    for filepath in HTML_FILES:
        try:
            if update_html(filepath, am_data, amg7_data, spy_data):
                changed = True
        except FileNotFoundError:
            print(f"  {filepath}: file not found, skipping")

    if changed:
        print("Done - files updated.")
    else:
        print("Done - no changes needed.")


if __name__ == "__main__":
    main()
