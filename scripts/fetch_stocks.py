import csv
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

import yfinance as yf

SCRIPT_DIR = Path(__file__).parent
CSV_PATH = SCRIPT_DIR / "../data/stocks_list.csv"
OUTPUT_PATH = SCRIPT_DIR / "../data/stocks.json"
ANOMALY_YIELD_THRESHOLD = 20.0
MA_PERIOD = "4mo"
JST = timezone(timedelta(hours=9))


def read_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                rows.append((row[0].strip(), row[1].strip()))
    return rows


def now_jst():
    return datetime.now(JST).isoformat(timespec="seconds")


def fetch_vix():
    try:
        ticker = yf.Ticker("^VIX")
        price = ticker.fast_info.last_price
        return {"vix": round(float(price), 2), "vix_updated": now_jst()}
    except Exception as e:
        print(f"  VIX 取得失敗: {e}")
        return {"vix": None, "vix_updated": None}


def get_balance_sheet_value(bs, keys):
    for key in keys:
        if key in bs.index:
            try:
                val = bs.loc[key].iloc[0]
                if val is not None and str(val) != "nan":
                    return float(val)
            except Exception:
                pass
    return None


def normalize_series(values):
    if not values:
        return []
    base = abs(values[0]) if values[0] != 0 else 1
    return [round(v / base * 100) for v in values]


def fetch_one(code, name_ja):
    ticker_str = f"{code}.T"
    result = {
        "code": code,
        "name_ja": name_ja,
        "sector_ja": None,
        "sector_en": None,
        "price": None,
        "prev_close": None,
        "day_change_pct": None,
        "yield": None,
        "yield_error": False,
        "annual_dividend": None,
        "market_cap": None,
        "per": None,
        "pbr": None,
        "op_margin": None,
        "payout_ratio": None,
        "equity_ratio": None,
        "revenue_trend": [],
        "eps_trend": [],
        "cash_trend": [],
        "op_cashflow": None,
        "dividend_history": [],
        "high_52w": None,
        "low_52w": None,
        "ma25": None,
        "ma75": None,
        "error": None,
    }
    try:
        t = yf.Ticker(ticker_str)
        info = t.info

        # 株価・前日比
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
        result["price"] = price
        result["prev_close"] = prev_close
        if price and prev_close and prev_close != 0:
            result["day_change_pct"] = round((price - prev_close) / prev_close * 100, 2)

        # 配当利回り
        raw_yield = info.get("dividendYield")
        if raw_yield is not None:
            pct = round(float(raw_yield) * 100, 2)
            result["yield"] = pct
            if pct >= ANOMALY_YIELD_THRESHOLD:
                result["yield_error"] = True
        result["annual_dividend"] = info.get("dividendRate")

        # バリュー指標
        result["market_cap"] = info.get("marketCap")
        result["per"] = info.get("trailingPE")
        result["pbr"] = info.get("priceToBook")
        result["sector_en"] = info.get("sector", "") or ""

        # 財務指標（デシマル → %）
        op_margin = info.get("operatingMargins")
        if op_margin is not None:
            result["op_margin"] = round(float(op_margin) * 100, 2)

        payout = info.get("payoutRatio")
        if payout is not None:
            payout_f = float(payout)
            if payout_f <= 2.0:  # > 200% はバグ値
                result["payout_ratio"] = round(payout_f * 100, 2)

        # 自己資本比率 (B/S)
        try:
            bs = t.balance_sheet
            if bs is not None and not bs.empty:
                equity = get_balance_sheet_value(bs, [
                    "Stockholders Equity",
                    "Total Stockholders Equity",
                    "Common Stock Equity",
                ])
                assets = get_balance_sheet_value(bs, [
                    "Total Assets",
                ])
                if equity is not None and assets and assets != 0:
                    result["equity_ratio"] = round(equity / assets * 100, 2)

                # 現金推移
                cash_vals = []
                for key in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
                    if key in bs.index:
                        series = bs.loc[key].dropna().sort_index()
                        cash_vals = [float(v) for v in series.values[-3:]]
                        break
                result["cash_trend"] = normalize_series(cash_vals)
        except Exception:
            pass

        # 損益計算書（売上・EPS）
        try:
            fin = t.financials
            if fin is not None and not fin.empty:
                # 売上推移
                for rev_key in ["Total Revenue", "Operating Revenue"]:
                    if rev_key in fin.index:
                        series = fin.loc[rev_key].dropna().sort_index()
                        vals = [float(v) for v in series.values[-3:]]
                        result["revenue_trend"] = normalize_series(vals)
                        break
                # EPS推移
                for eps_key in ["Basic EPS", "Diluted EPS"]:
                    if eps_key in fin.index:
                        series = fin.loc[eps_key].dropna().sort_index()
                        vals = [float(v) for v in series.values[-3:]]
                        result["eps_trend"] = normalize_series(vals)
                        break
        except Exception:
            pass

        # 営業キャッシュフロー
        try:
            cf = t.cashflow
            if cf is not None and not cf.empty:
                for cf_key in ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]:
                    if cf_key in cf.index:
                        val = cf.loc[cf_key].iloc[0]
                        if val is not None and str(val) != "nan":
                            result["op_cashflow"] = float(val)
                        break
        except Exception:
            pass

        # 配当履歴（直近3年）
        try:
            divs = t.dividends
            if divs is not None and not divs.empty:
                if divs.index.tz is not None:
                    divs.index = divs.index.tz_localize(None)
                annual = divs.resample("YE").sum().tail(3)
                result["dividend_history"] = [round(float(v), 1) for v in annual.values.tolist()]
        except Exception:
            pass

        # 52週高値・安値
        result["high_52w"] = info.get("fiftyTwoWeekHigh")
        result["low_52w"] = info.get("fiftyTwoWeekLow")

        # 移動平均（4ヶ月分の日次終値）
        try:
            hist = t.history(period=MA_PERIOD)
            if hist is not None and not hist.empty:
                closes = hist["Close"]
                if len(closes) >= 25:
                    result["ma25"] = round(float(closes.tail(25).mean()), 1)
                if len(closes) >= 75:
                    result["ma75"] = round(float(closes.tail(75).mean()), 1)
        except Exception:
            pass

    except Exception as e:
        result["error"] = str(e)
        print(f"  エラー: {e}")

    return result


def main():
    stocks_meta = read_csv(CSV_PATH)
    print(f"取得対象: {len(stocks_meta)} 銘柄")

    vix_data = fetch_vix()
    print(f"VIX: {vix_data['vix']}")

    results = []
    for i, (code, name_ja) in enumerate(stocks_meta, 1):
        print(f"[{i}/{len(stocks_meta)}] {code} {name_ja} ...")
        data = fetch_one(code, name_ja)
        results.append(data)
        time.sleep(0.5)

    output = {
        "meta": {
            "updated": now_jst(),
            "vix": vix_data["vix"],
            "vix_updated": vix_data["vix_updated"],
        },
        "stocks": results,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    errors = [s for s in results if s.get("error")]
    print(f"\n完了: {len(results)} 銘柄 (エラー {len(errors)} 件)")
    if errors:
        print("エラー銘柄:", [s["code"] for s in errors])


if __name__ == "__main__":
    main()
