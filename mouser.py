import requests
import json


def getdata(pn):
    # Swagger API 文件中的路徑和參數
    url = 'https://api.mouser.com/api/v1/search/partnumber?apiKey=8b1390e5-5fbc-4169-9c88-ac16c0599220'
    api_key = '8b1390e5-5fbc-4169-9c88-ac16c0599220'
    api_key_order = '19c5e8f6-6454-4387-bbbd-fbfa3b4d1434'

    # 設定請求的 headers，如果需要 API 金鑰
    headers = {
        'Authorization': f'Bearer {api_key_order}',
        'Content-Type': 'application/json'
    }

    data = {
        "SearchByPartRequest": {
            "mouserPartNumber": pn,
            "partSearchOptions": "string"
        }
    }

    response = requests.post(url,headers=headers,json=data)

    # 解析回應內容
    response_content = response.json()
    # 檢查回應是否包含 SearchResults
    if 'SearchResults' in response_content:
        parts = response_content['SearchResults']['Parts']
        parts_info = []
        # 逐個處理每個部分
        for part in parts:
            availability = part.get('Availability')
            manufacturer = part.get('Manufacturer')
            manufacturer_part_number = part.get('ManufacturerPartNumber')
            price_breaks = part.get('PriceBreaks', [])
            image_Link = part.get('ImagePath')
            ProductDetail_Url = part.get('ProductDetailUrl')
            part_info = {
            'Availability': availability,
            'Manufacturer': manufacturer,
            'ManufacturerPartNumber': manufacturer_part_number,
            'PriceBreaks': price_breaks,
            'image_Link': image_Link,
            'ProductDetail_Url': ProductDetail_Url
            }  
            parts_info.append(part_info)          
        return {"data": parts_info}
    else:
        return {"data":"nodata"}

