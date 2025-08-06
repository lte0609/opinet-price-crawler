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
        raw_date = oil_entry.findtext('DATE')
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
    dates_sorted = sorted(prices_by_date.keys())
    last_date = dates_sorted[-1]
    year_month = last_date[:7]
    output = {
        "month": year_month,
        "prices_by_date": prices_by_date
    }
    filename = f"{year_month}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved data to {filename}")

def main():
    xml_data = fetch_opinet_data()
    prices_by_date = parse_xml_and_extract_prices(xml_data)
    save_prices_json(prices_by_date)

if __name__ == "__main__":
    main()
