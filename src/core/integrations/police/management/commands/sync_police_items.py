import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand, CommandError
from decouple import config
from datetime import datetime

from core.integrations.police.models import PoliceFoundItem # 새로 정의한 모델 임포트

class Command(BaseCommand):
    help = 'Fetches police found items from the external API and saves them to the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting police found items synchronization...'))

        api_key = config('POLICE_API_KEY', default=None)
        if not api_key:
            raise CommandError('POLICE_API_KEY is not set in environment variables or .env file.')

        base_url = 'http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd'
        page_no = 1
        num_of_rows = 100 # 한 번에 가져올 항목 수
        total_count = 0
        items_processed = 0
        items_created = 0
        items_updated = 0

        while True:
            params = {
                'serviceKey': api_key,
                'pageNo': page_no,
                'numOfRows': num_of_rows,
            }

            try:
                response = requests.get(base_url, params=params, timeout=60)
                response.raise_for_status() # HTTP 오류 발생 시 예외 발생

                root = ET.fromstring(response.content)
                
                result_code = root.findtext('.//resultCode')
                if result_code != '00':
                    result_msg = root.findtext('.//resultMsg')
                    self.stdout.write(self.style.ERROR(f"API Error: {result_msg} (Code: {result_code})"))
                    break # 오류 발생 시 중단

                # 첫 페이지에서만 totalCount를 가져옴
                if page_no == 1:
                    total_count_node = root.find('.//totalCount')
                    if total_count_node is not None and total_count_node.text and total_count_node.text.isdigit():
                        total_count = int(total_count_node.text)
                    self.stdout.write(self.style.SUCCESS(f"Total items to process: {total_count}"))

                item_nodes = root.findall('.//item')
                if not item_nodes: # 더 이상 가져올 항목이 없으면 중단
                    self.stdout.write(self.style.SUCCESS('No more items to fetch. Synchronization complete.'))
                    break

                for item_node in item_nodes:
                    atc_id = item_node.findtext('atcId')
                    fd_ymd_str = item_node.findtext('fdYmd')
                    fd_ymd = None
                    if fd_ymd_str:
                        try:
                            fd_ymd = datetime.strptime(fd_ymd_str, '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Invalid date format for atcId {atc_id}: {fd_ymd_str}"))

                    defaults = {
                        'clrNm': item_node.findtext('clrNm'),
                        'depPlace': item_node.findtext('depPlace'),
                        'fdFilePathImg': item_node.findtext('fdFilePathImg'),
                        'fdPrdtNm': item_node.findtext('fdPrdtNm'),
                        'fdSbjt': item_node.findtext('fdSbjt'),
                        'fdSn': int(item_node.findtext('fdSn')) if item_node.findtext('fdSn') else None,
                        'fdYmd': fd_ymd,
                        'prdtClNm': item_node.findtext('prdtClNm'),
                    }

                    # atcId를 기준으로 기존 항목을 찾거나 새로 생성
                    obj, created = PoliceFoundItem.objects.update_or_create(
                        atcId=atc_id,
                        defaults=defaults
                    )

                    if created:
                        items_created += 1
                    else:
                        items_updated += 1
                    items_processed += 1

                self.stdout.write(self.style.SUCCESS(f"Page {page_no} processed. Total processed: {items_processed}/{total_count}"))
                page_no += 1

                # 모든 항목을 가져왔거나, 너무 많은 페이지를 처리하는 것을 방지 (선택적)
                if items_processed >= total_count or page_no > (total_count / num_of_rows) + 10: # 안전 장치
                    self.stdout.write(self.style.SUCCESS('Reached total count or page limit. Synchronization complete.'))
                    break

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"API request failed: {e}"))
                break
            except ET.ParseError:
                self.stdout.write(self.style.ERROR('Failed to parse XML response.'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
                break

        self.stdout.write(self.style.SUCCESS(f'Synchronization finished. Created: {items_created}, Updated: {items_updated}, Total Processed: {items_processed}'))
