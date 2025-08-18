import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views import View
from decouple import config

class PoliceFoundItemsView(View):
    def get(self, request):
        try:
            # .env 파일에서 API 키를 안전하게 불러옵니다.
            api_key = config('POLICE_API_KEY')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'POLICE_API_KEY가 .env 파일에 설정되지 않았습니다.'}, status=500)

        params = {
            'serviceKey': api_key,
            'pageNo': request.GET.get('pageNo', '1'),
            'numOfRows': request.GET.get('numOfRows', '10'),
        }

        try:
            response = requests.get(
                'http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd',
                params=params,
                timeout=10
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            
            # API 에러 응답 처리 (공공데이터포털 표준)
            result_code = root.findtext('.//resultCode')
            if result_code != '00':
                result_msg = root.findtext('.//resultMsg')
                return JsonResponse({'status': 'error', 'message': f'API Error: {result_msg} (Code: {result_code})'}, status=400)

            items = []
            for item_node in root.findall('.//item'):
                item_data = {
                    'atcId': item_node.findtext('atcId'),
                    'depPlace': item_node.findtext('depPlace'),
                    'fdPrdtNm': item_node.findtext('fdPrdtNm'),
                    'fdYmd': item_node.findtext('fdYmd'),
                    'fdFilePathImg': item_node.findtext('fdFilePathImg'),
                    'prdtClCd01': item_node.findtext('prdtClCd01'),
                    'prdtClCd02': item_node.findtext('prdtClCd02'),
                    'fdSn': item_node.findtext('fdSn'),
                }
                items.append(item_data)
            
            total_count_node = root.find('.//totalCount')
            total_count = int(total_count_node.text) if total_count_node is not None else 0

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
            return JsonResponse({'status': 'error', 'message': 'Failed to parse XML response'}, status=500)