import csv
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CSV_PATH = SCRIPT_DIR / "../data/stocks_list.csv"
JSON_PATH = SCRIPT_DIR / "../data/stocks.json"

SECTOR_MAP = {
    # 金融
    "Financial Services": "金融サービス",
    "Financial": "金融サービス",
    "Diversified Financial Services": "多角的金融サービス",
    "Insurance": "保険",
    "Insurance—Life": "生命保険",
    "Insurance—Property & Casualty": "損害保険",
    "Insurance—Diversified": "保険（複合）",
    "Banks": "銀行",
    "Banking": "銀行",
    "Banks—Regional": "地方銀行",
    "Banks—Diversified": "銀行（複合）",
    "Asset Management": "資産運用",
    "Capital Markets": "資本市場",
    "Credit Services": "クレジットサービス",
    "Mortgage Finance": "住宅ローン",
    # 産業・製造
    "Industrials": "産業・機械",
    "Industrial Conglomerates": "複合産業",
    "Conglomerates": "コングロマリット",
    "Machinery": "機械",
    "Farm & Construction Equipment": "農業・建設機械",
    "Farm & Heavy Construction Machinery": "農業・建設機械",
    "Construction & Engineering": "建設・エンジニアリング",
    "Engineering & Construction": "建設・エンジニアリング",
    "Building Products": "建設資材",
    "Building Materials": "建設資材",
    "Electrical Equipment & Parts": "電気設備",
    "Diversified Industrials": "複合産業",
    "Industrial Distribution": "産業卸売",
    "Tools & Accessories": "工具・部品",
    "Aerospace & Defense": "航空宇宙・防衛",
    "Waste Management": "廃棄物管理",
    "Environmental Services": "環境サービス",
    "Security & Protection Services": "セキュリティサービス",
    "Staffing & Employment Services": "人材サービス",
    "Consulting Services": "コンサルティング",
    "Business Services": "ビジネスサービス",
    "Research & Development Services": "研究開発サービス",
    "Rental & Leasing Services": "レンタル・リース",
    "Specialty Business Services": "専門ビジネスサービス",
    # 輸送・物流
    "Transportation Infrastructure": "輸送インフラ",
    "Air Freight & Logistics": "航空貨物・物流",
    "Integrated Freight & Logistics": "物流（統合）",
    "Marine Shipping": "海運",
    "Marine": "海運",
    "Trucking": "トラック輸送",
    "Railroads": "鉄道",
    "Airlines": "航空",
    "Airport Services": "空港サービス",
    "Road & Rail": "陸運",
    "Shipping & Ports": "海運・港湾",
    "Courier & Delivery Services": "宅配便",
    # テクノロジー
    "Technology": "情報技術",
    "Information Technology": "情報技術",
    "Information Technology Services": "ITサービス",
    "IT Services": "ITサービス",
    "Software—Application": "ソフトウェア（アプリ）",
    "Software—Infrastructure": "ソフトウェア（インフラ）",
    "Software": "ソフトウェア",
    "Electronic Equipment, Instruments & Components": "電子部品",
    "Electronic Components": "電子部品",
    "Electronics & Computer Distribution": "電子機器流通",
    "Semiconductors": "半導体",
    "Semiconductors & Semiconductor Equipment": "半導体",
    "Hardware, Equipment & Supplies": "電子機器",
    "Computer Hardware": "コンピュータ機器",
    "Communication Equipment": "通信機器",
    "Scientific & Technical Instruments": "精密機器",
    "Specialty Industrial Machinery": "特殊産業機械",
    "Industrial Machinery": "産業機械",
    # 消費財
    "Consumer Cyclical": "消費財（景気敏感）",
    "Consumer Discretionary": "消費財（景気敏感）",
    "Consumer Defensive": "消費財（ディフェンシブ）",
    "Consumer Staples": "消費財（ディフェンシブ）",
    "Retail—Specialty": "専門小売",
    "Specialty Retail": "専門小売",
    "Retail—Apparel": "アパレル小売",
    "Apparel Retail": "アパレル小売",
    "Apparel Manufacturing": "アパレル製造",
    "Footwear & Accessories": "靴・アクセサリー",
    "Auto & Truck Dealerships": "自動車販売",
    "Auto Manufacturers": "自動車",
    "Auto Parts": "自動車部品",
    "Recreational Vehicles": "レジャー用車両",
    "Household Durables": "家庭用耐久財",
    "Home Improvement Retail": "ホームセンター",
    "Furnishings, Fixtures & Appliances": "家具・家電",
    "Household & Personal Products": "家庭・個人用品",
    "Personal Products": "パーソナルケア",
    "Leisure": "レジャー",
    "Travel & Leisure": "旅行・レジャー",
    "Hotels, Resorts & Cruise Lines": "ホテル・リゾート",
    "Restaurants": "外食",
    "Education & Training Services": "教育・研修",
    "Department Stores": "百貨店",
    "Discount Stores": "ディスカウント",
    "Internet Retail": "ネット通販",
    "Grocery Stores": "食料品小売",
    "Drug Stores": "ドラッグストア",
    "Specialty Chemicals": "特殊化学品",
    # 食品・飲料
    "Food Distribution": "食品流通",
    "Food Products": "食品",
    "Packaged Foods": "加工食品",
    "Confectioners": "菓子",
    "Beverages—Non-Alcoholic": "飲料（非アルコール）",
    "Beverages—Alcoholic": "飲料（アルコール）",
    "Beverages—Brewers": "ビール",
    "Tobacco": "タバコ",
    "Agricultural Products": "農産物",
    "Agricultural Inputs": "農業資材",
    "Farm Products": "農産物",
    # ヘルスケア
    "Healthcare": "医薬品・医療",
    "Health Care": "医薬品・医療",
    "Drug Manufacturers—General": "医薬品（大手）",
    "Drug Manufacturers—Specialty & Generic": "医薬品（特殊・後発）",
    "Biotechnology": "バイオテクノロジー",
    "Medical Devices": "医療機器",
    "Medical Distribution": "医療流通",
    "Health Care Plans": "医療保険",
    "Diagnostics & Research": "診断・研究",
    "Medical Care Facilities": "医療施設",
    "Medical Instruments & Supplies": "医療機器・消耗品",
    "Health Information Services": "医療情報サービス",
    "Pharmaceutical Retailers": "薬局",
    # 不動産
    "Real Estate": "不動産",
    "Real Estate Services": "不動産サービス",
    "Real Estate—Development": "不動産開発",
    "Real Estate—Diversified": "不動産（複合）",
    "REIT—Office": "REIT（オフィス）",
    "REIT—Residential": "REIT（住宅）",
    "REIT—Retail": "REIT（商業）",
    "REIT—Industrial": "REIT（物流）",
    "REIT—Diversified": "REIT（総合）",
    "REIT—Hotel & Motel": "REIT（ホテル）",
    "REIT—Healthcare Facilities": "REIT（ヘルスケア）",
    "REIT—Mortgage": "REIT（モーゲージ）",
    "REIT—Specialty": "REIT（特殊）",
    # 通信
    "Communication Services": "通信サービス",
    "Telecom Services": "通信サービス",
    "Telecommunications Services": "通信サービス",
    "Telephone & Telegraph": "電話・通信",
    "Internet Content & Information": "インターネット",
    "Electronic Gaming & Multimedia": "ゲーム・メディア",
    "Broadcasting": "放送",
    "Publishing": "出版",
    "Entertainment": "エンターテインメント",
    "Advertising Agencies": "広告",
    # エネルギー
    "Energy": "エネルギー",
    "Oil & Gas E&P": "石油・ガス（探鉱）",
    "Oil & Gas Integrated": "石油・ガス（総合）",
    "Oil & Gas Midstream": "石油・ガス（輸送）",
    "Oil & Gas Refining & Marketing": "石油・ガス（精製）",
    "Oil & Gas Drilling": "石油・ガス（掘削）",
    "Oil & Gas Equipment & Services": "石油・ガス（機器）",
    # 素材・化学
    "Basic Materials": "素材・化学",
    "Materials": "素材・化学",
    "Chemicals": "化学",
    "Specialty Chemicals": "特殊化学品",
    "Agricultural Inputs": "農業資材",
    "Rubber & Plastics": "ゴム・プラスチック",
    "Industrial Metals & Mining": "金属・鉱業",
    "Steel": "鉄鋼",
    "Aluminum": "アルミニウム",
    "Copper": "銅",
    "Gold": "金",
    "Silver": "銀",
    "Other Precious Metals & Mining": "貴金属・鉱業",
    "Coking Coal": "コークス炭",
    "Thermal Coal": "石炭",
    "Paper & Paper Products": "紙・パルプ",
    "Lumber & Wood Production": "木材",
    "Other Industrial Metals & Mining": "その他金属・鉱業",
    "Construction Materials": "建設資材",
    "Glass & Ceramics Products": "ガラス・セラミック",
    "Packaging & Containers": "包装・容器",
    # 公益
    "Utilities": "公益事業",
    "Electric Utilities": "電力",
    "Gas Utilities": "ガス",
    "Water Utilities": "水道",
    "Utilities—Regulated Electric": "電力（規制）",
    "Utilities—Regulated Gas": "ガス（規制）",
    "Utilities—Regulated Water": "水道（規制）",
    "Utilities—Diversified": "公益事業（複合）",
    "Utilities—Independent Power Producers": "独立発電事業者",
    "Utilities—Renewable": "再生可能エネルギー",
}

SECTOR_FALLBACK = "その他"


def main():
    # CSV から名前辞書を構築
    name_ja_dict = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                name_ja_dict[row[0].strip()] = row[1].strip()

    # JSON を読み込んでパッチ
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for stock in data.get("stocks", []):
        code = stock.get("code", "")
        if code in name_ja_dict:
            stock["name_ja"] = name_ja_dict[code]

        sector_en = stock.pop("sector_en", "") or ""
        stock["sector_ja"] = SECTOR_MAP.get(sector_en, SECTOR_FALLBACK if sector_en else None)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"translate_names.py 完了: {len(data.get('stocks', []))} 銘柄を処理")


if __name__ == "__main__":
    main()
