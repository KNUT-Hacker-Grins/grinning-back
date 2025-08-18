import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views import View
from decouple import config

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
            # Enable streaming for memory efficiency
            response = requests.get(
                'http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd',
                params=params,
                timeout=60,
                stream=True
            )
            response.raise_for_status()

            # Use iterparse for memory-efficient XML parsing
            context = ET.iterparse(response.raw, events=('end',))
            items = []
            total_count = 0
            
            for _, elem in context:
                if elem.tag == 'item':
                    items.append({
                        'atcId': elem.findtext('atcId'),
                        'depPlace': elem.findtext('depPlace'),
                        'fdPrdtNm': elem.findtext('fdPrdtNm'),
                        'fdYmd': elem.findtext('fdYmd'),
                        'fdFilePathImg': elem.findtext('fdFilePathImg'),
                        'prdtClNm': elem.findtext('prdtClNm'),
                        'clrNm': elem.findtext('clrNm'),
                        'fdSn': elem.findtext('fdSn'),
                    })
                elif elem.tag == 'totalCount':
                    if elem.text and elem.text.isdigit():
                        total_count = int(elem.text)
                elif elem.tag == 'resultCode' and elem.text != '00':
                    return JsonResponse({'status': 'error', 'message': f"API returned error code: {elem.text}"}, status=400)
                
                # Free memory
                elem.clear()

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
