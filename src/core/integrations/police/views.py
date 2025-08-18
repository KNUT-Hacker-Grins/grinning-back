import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views import View
from decouple import config

import gzip

class PoliceFoundItemsView(View):
    def get(self, request):
        try:
            api_key = config('POLICE_API_KEY')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'POLICE_API_KEY가 .env 파일에 설정되지 않았습니다.'}, status=500)

        params = {
            'serviceKey': api_key,
            'pageNo': request.GET.get('pageNo', '1'),
            'numOfRows': request.GET.get('numOfRows', '10'),
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(
                'http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd',
                params=params,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()

            try:
                decompressed_content = gzip.decompress(response.content)
            except gzip.BadGzipFile as e:
                print(f"[GZIP DECOMPRESSION FAILED]: {e}")
                print(f"[RAW RESPONSE CONTENT (first 500 bytes)]: {response.content[:500]}")
                return JsonResponse({'status': 'error', 'message': 'Failed to decompress API response.'}, status=500)

            root = ET.fromstring(decompressed_content)
            
            result_code = root.findtext('.//resultCode')
            if result_code is not None and result_code != '00':
                result_msg = root.findtext('.//resultMsg')
                error_message = f"API Error: {result_msg} (Code: {result_code})"
                return JsonResponse({'status': 'error', 'message': error_message}, status=400)

            items = []
            for item_node in root.findall('.//item'):
                item_data = {
                    'atcId': item_node.findtext('atcId'),
                    'depPlace': item_node.findtext('depPlace'),
                    'fdPrdtNm': item_node.findtext('fdPrdtNm'),
                    'fdYmd': item_node.findtext('fdYmd'),
                    'fdFilePathImg': item_node.findtext('fdFilePathImg'),
                    'prdtClNm': item_node.findtext('prdtClNm'),
                    'clrNm': item_node.findtext('clrNm'),
                    'fdSn': item_node.findtext('fdSn'),
                }
                items.append(item_data)
            
            total_count_node = root.find('.//totalCount')
            total_count = 0
            if total_count_node is not None and total_count_node.text and total_count_node.text.isdigit():
                total_count = int(total_count_node.text)

            return JsonResponse({
                'status': 'success',
                'data': {
                    'items': items,
                    'total': total_count,
                    'page': int(params['pageNo']),
                }
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': f'API request failed: {e}'}, status=500)
        except ET.ParseError:
            return JsonResponse({'status': 'error', 'message': 'Failed to parse XML response (possibly HTML or malformed XML)'}, status=500)
