import xml.etree.ElementTree as ET


def parse_sms_xml(xml_path):
 
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records = []
    for idx, sms in enumerate(root.findall("sms"), start=1):
        records.append({
            "id": idx,
            "address": sms.get("address"),
            "body": sms.get("body", "") or "",
            "date": sms.get("date"),
            "readable_date": sms.get("readable_date"),
        })
    return records


if __name__ == "__main__":
    from config import RAW_XML_PATH
    data = parse_sms_xml(RAW_XML_PATH)
    print(f"Parsed {len(data)} raw SMS records from {RAW_XML_PATH}")
    if data:
        print("Sample record:", data[0])
