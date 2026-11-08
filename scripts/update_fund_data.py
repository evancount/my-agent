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


# ---------------- Multi-fund simulator data ----------------

CNYES_NAV_URL = "https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/nav"
CNYES_PERF_URL = "https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/history/performance"
MULTI_DATA_FILE = "multi-fund-data.js"

MULTI_FUNDS = [
    # 配息型
    {"key": "allianz_am",   "cnyes": "B20,073", "type": "div", "ccy": "USD", "name": "安聯收益成長基金 AM 穩定月收類股（美元）"},
    {"key": "allianz_amg7", "cnyes": "B2abw8B", "type": "div", "ccy": "USD", "name": "安聯收益成長基金 AMg7 月收總收益類股（美元）"},
    {"key": "jpm_income",   "cnyes": "B080291", "type": "div", "ccy": "USD", "name": "摩根多重收益基金（美元對沖）A股（穩定月配）"},
    {"key": "br_data_inc",  "cnyes": "B09,325", "type": "div", "ccy": "USD", "name": "貝萊德全球智慧數據股票入息基金 A6 美元（穩定配息）"},
    {"key": "br_tech_a10",  "cnyes": "B090460", "type": "div", "ccy": "USD", "name": "貝萊德世界科技基金 A10 美元（總報酬穩定配息）"},
    {"key": "br_fin_a10",   "cnyes": "B090459", "type": "div", "ccy": "USD", "name": "貝萊德世界金融基金 A10 美元（總報酬穩定配息）"},
    {"key": "ab_us_growth", "cnyes": "B030870", "type": "div", "ccy": "USD", "name": "聯博美國成長基金 AP（總報酬月配）美元"},
    {"key": "inv_tech_m8",  "cnyes": "A06128",  "type": "div", "ccy": "TWD", "name": "景順全球科技基金 M8 月配息型（新台幣）"},
    {"key": "eastspring",   "cnyes": "A1ftj5w", "type": "div", "ccy": "USD", "name": "瀚亞多重收益優化組合基金 B類型（美元）"},
    {"key": "ft_income",    "cnyes": "B15,108", "type": "div", "ccy": "USD", "name": "富蘭克林坦伯頓穩定月收益基金 美元A (Mdis)"},
    # 累積型
    {"key": "br_tech_a2",   "cnyes": "B09,005", "type": "acc", "ccy": "USD", "name": "貝萊德世界科技基金 A2（美元）"},
    {"key": "br_fin_a2",    "cnyes": "B09,102", "type": "acc", "ccy": "USD", "name": "貝萊德世界金融基金 A2（美元）"},
    {"key": "allianz_twtech", "cnyes": "A36004", "type": "acc", "ccy": "TWD", "name": "安聯台灣科技基金（新台幣）"},
    {"key": "allianz_twdam",  "cnyes": "A36001", "type": "acc", "ccy": "TWD", "name": "安聯台灣大壩基金 A類型（新台幣）"},
    {"key": "schroder_cycle", "cnyes": "A16IYCv", "type": "acc", "ccy": "TWD", "name": "施羅德全週期成長多重資產基金 A累積型（新台幣）"},
]

DAY = 86400
WINDOW = 3650 * DAY  # performance endpoint returns at most ~10 years per call


def _get(url, **params):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()["items"]


def nav_table(fund_id, **params):
    rows = _get(CNYES_NAV_URL.format(fund_id=fund_id), format="table", page=1, **params)["data"]
    return {r["tradeDate"]: float(r["nav"]) for r in rows}


def perf_window(fund_id, end):
    """Up to 10 years of daily performance ending at `end`.

    The endpoint returns nothing when the window starts before the fund's
    inception, so the start is moved forward a year at a time until data appears.
    """
    start = end - WINDOW
    while start < end - 30 * DAY:
        items = _get(CNYES_PERF_URL.format(fund_id=fund_id), by="d", startAt=start, endAt=end)
        window = {t: 1 + p / 100 for t, p in zip(items["tradeDate"], items["performance"])}
        if len(window) >= 2:
            return window, start
        start += 365 * DAY
    return {}, start


def fetch_nav_series(fund_id):
    """Daily NAV {ts: nav}, rebuilt from chained 10-year performance windows."""
    recent = nav_table(fund_id)
    index = {}
    end = max(recent) + DAY
    while True:
        window, start = perf_window(fund_id, end)
        if not window:
            break
        if index:
            common = sorted(set(window) & set(index))
            if not common:
                break
            link = common[-1]
            scale = index[link] / window[link]
            window = {t: v * scale for t, v in window.items() if t < min(index)}
            if not window:
                break
        index.update(window)
        if start > end - WINDOW:
            break  # window was shortened, so it reached inception
        end = min(index)
    if not index:
        raise RuntimeError(f"{fund_id}: no performance data")
    last = max(index)
    actual = nav_table(fund_id, startAt=last - 10 * DAY, endAt=last + DAY)
    anchor = max(t for t in actual if t <= last)
    near = min(index, key=lambda t: abs(t - anchor))
    scale = actual[anchor] / index[near]
    series = {t: v * scale for t, v in index.items()}
    series.update({t: v for t, v in recent.items() if t > last})
    return series


def month_end_series(daily):
    """{ts: value} -> {"YYYY-MM": value} using the last trading day of each month."""
    out = {}
    for t in sorted(daily):
        ym = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m")
        out[ym] = daily[t]
    return out


def dividend_months(fund_id):
    """{"YYYY-MM": [nav, dividend]} from ex-dividend records."""
    out = {}
    for r in dividends_to_js_array(fetch_all_dividends(fund_id)):
        ym = r["date"][:7]
        if ym in out:
            out[ym][1] = round(out[ym][1] + r["dividend"], 5)
            out[ym][0] = r["nav"]
        else:
            out[ym] = [r["nav"], r["dividend"]]
    return out


def yahoo_monthly(ticker, start="2003-01-01"):
    import yfinance as yf
    hist = yf.Ticker(ticker).history(start=start, interval="1mo")
    return {idx.strftime("%Y-%m"): round(float(row["Close"]), 4) for idx, row in hist.iterrows()}


def build_multi_fund_data():
    funds = []
    for f in MULTI_FUNDS:
        if f["type"] == "div":
            data = dividend_months(f["cnyes"])
        else:
            data = {ym: [round(v, 4), 0] for ym, v in month_end_series(fetch_nav_series(f["cnyes"])).items()}
        if not data:
            raise RuntimeError(f"No data for {f['name']} ({f['cnyes']})")
        months = sorted(data)
        print(f"  {f['name']}: {len(months)} months {months[0]} ~ {months[-1]}")
        funds.append({**f, "data": data})

    spy = yahoo_monthly("SPY")
    funds.append({"key": "spy", "cnyes": "", "type": "acc", "ccy": "USD",
                  "name": "S&P 500 ETF（SPY，含息）", "data": {ym: [v, 0] for ym, v in spy.items()}})
    fx = yahoo_monthly("TWD=X")
    print(f"  SPY: {len(spy)} months, USD/TWD: {len(fx)} months")

    payload = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "fx": fx, "funds": funds}
    js = "window.FUND_DB = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    try:
        with open(MULTI_DATA_FILE, encoding="utf-8") as fh:
            old = fh.read()
    except FileNotFoundError:
        old = ""
    if re.sub(r'"updated":"[^"]*"', "", old) == re.sub(r'"updated":"[^"]*"', "", js):
        print(f"  {MULTI_DATA_FILE}: no changes")
        return False
    with open(MULTI_DATA_FILE, "w", encoding="utf-8") as fh:
        fh.write(js)
    print(f"  {MULTI_DATA_FILE}: updated")
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

    print("Building multi-fund simulator data...")
    if build_multi_fund_data():
        changed = True

    if changed:
        print("Done - files updated.")
    else:
        print("Done - no changes needed.")


if __name__ == "__main__":
    main()
