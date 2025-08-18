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
            response = requests.get(
                'http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd',
                params=params,
                timeout=10
            )
            
            print(f"Police API Response Status Code: {response.status_code}") # 상태 코드 출력
            print(f"Police API Raw Response Content: {response.content.decode('utf-8')}") # 원본 내용 출력

            response.raise_for_status() # 200 OK가 아니면 여기서 예외 발생

            root = ET.fromstring(response.content)
            
            # 공공데이터포털 표준 오류 응답 XML 구조에 맞춰 파싱
            cmm_msg_header = root.find('.//cmmMsgHeader')
            if cmm_msg_header is not None:
                return_reason_code = cmm_msg_header.findtext('returnReasonCode')
                return_auth_msg = cmm_msg_header.findtext('returnAuthMsg')
                err_msg = cmm_msg_header.findtext('errMsg')

                if return_reason_code and return_reason_code != '00':
                    error_message = f"API Error: {err_msg or return_auth_msg} (Code: {return_reason_code})"
                    return JsonResponse({'status': 'error', 'message': error_message}, status=400)
            
            # 정상 응답의 resultCode 확인 (이전 로직 유지)
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
            return JsonResponse({'status': 'error', 'message': 'Failed to parse XML response (possibly HTML or malformed XML)'}, status=500)
