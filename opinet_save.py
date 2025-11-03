import requests
import xml.etree.ElementTree as ET
import datetime
import json

PRODUCT_CODES = {
    "B027": "gasoline",  # 휘발유
    "D047": "diesel",    # 경유
    "K015": "lpg"        # LPG
}

def fetch_opinet_data():
    url = "https://www.opinet.co.kr/api/areaAvgRecentPrice.do"
    params = {
        "out": "xml",
        "code": "F250713595",
        "area": "05"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.content

def parse_xml_and_extract_prices(xml_data):
    root = ET.fromstring(xml_data)
    prices_by_date = {}
    for oil_entry in root.findall('OIL'):
        raw_date = oil_entry.findtext('DATE')  # YYYYMMDD
        date_str = datetime.datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d")
        prodcd = oil_entry.findtext('PRODCD')
        price = oil_entry.findtext('PRICE')
        if prodcd in PRODUCT_CODES:
            price_rounded = round(float(price))
            if date_str not in prices_by_date:
                prices_by_date[date_str] = {}
            prices_by_date[date_str][PRODUCT_CODES[prodcd]] = price_rounded
    return prices_by_date

def save_prices_json(prices_by_date):
    if not prices_by_date:
        print("No data to save")
        return

    # 가장 마지막 날짜 확인
    dates_sorted = sorted(prices_by_date.keys())
    last_date = dates_sorted[-1]               # 예: "2024-10-31"
    year_month = last_date[:7]                # 예: "2024-10"

    # 현재 시스템 날짜 기준 월 (한국 시간 기준 적용)
    now_kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    current_year_month = now_kst.strftime("%Y-%m")

    # ✅ 이번 달 데이터가 아니라면 저장하지 않음 (덮어쓰기 방지)
    if year_month != current_year_month:
        print(f"Skipped saving. API data is for {year_month}, but today is {current_year_month}.")
        return

    # 저장
    output = {
        "month": year_month,
        "prices_by_date": prices_by_date
    }
    filename = f"{year_month}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved data to {filename}")

def main():
    xml_data = fetch_opinet_data()
    prices_by_date = parse_xml_and_extract_prices(xml_data)
    save_prices_json(prices_by_date)

if __name__ == "__main__":
    main()
