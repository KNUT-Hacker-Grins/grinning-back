# C:\Users\cnblu\PycharmProjects\Unit6-back\src\core\integrations\police\management\commands\sync_police_lost_items.py

import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config

from core.integrations.police.models import PoliceLostItem # Changed model

class Command(BaseCommand):
    help = 'Fetches police lost items from the external API and saves them to the database.' # Changed help text

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting police lost items synchronization...')) # Changed log message

        api_key = config('POLICE_API_KEY', default=None)
        if not api_key:
            raise CommandError('POLICE_API_KEY is not set in environment variables or .env file.')

        # Assumption: The service URL for lost items is getLostThingInfoAccToClAreaPd
        # This needs to be verified from the actual API documentation.
        url = 'http://apis.data.go.kr/1320000/LostGoodsInfoInqireService/getLostGoodsInfoAccToClAreaPd'
        params = {
            'serviceKey': api_key,
            'pageNo': '1',
            'numOfRows': '1000' # Fetch a large number of items
        }

        try:
            response = requests.get(url, params=params, timeout=600)
            response.raise_for_status() # Raise an exception for bad status codes

            xml_data = response.content
            root = ET.fromstring(xml_data)

            items = root.findall('.//item')
            if not items:
                self.stdout.write(self.style.WARNING('No items found in the API response.'))
                return

            count = 0
            for item in items:
                # Assumption: XML tags for lost items use 'lst' prefix.
                # This needs to be verified from the actual API documentation.
                atcId = item.findtext('atcId')
                lstPlace = item.findtext('lstPlace', default='')
                lstFilePathImg = item.findtext('lstFilePathImg', default='')
                lstPrdtNm = item.findtext('lstPrdtNm', default='')
                lstSn = item.findtext('lstSn', default='')
                lstYmd = item.findtext('lstYmd', default='')
                prdtClNm = item.findtext('prdtClNm', default='')
                rnum = item.findtext('rnum')
                clrNm = item.findtext('clrNm', default='')
                tel = item.findtext('tel', default='')
                lstSbjt = item.findtext('lstSbjt', default='')

                if not atcId:
                    continue

                obj, created = PoliceLostItem.objects.update_or_create(
                    atcId=atcId,
                    defaults={
                        'lstPlace': lstPlace,
                        'lstFilePathImg': lstFilePathImg,
                        'lstPrdtNm': lstPrdtNm,
                        'lstSn': lstSn,
                        'lstYmd': lstYmd,
                        'prdtClNm': prdtClNm,
                        'rnum': int(rnum) if rnum else 0,
                        'clrNm': clrNm,
                        'tel': tel,
                        'lstSbjt': lstSbjt,
                    }
                )
                if created:
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully synchronized {count} new lost items.'))

        except requests.exceptions.RequestException as e:
            raise CommandError(f'Error fetching data from API: {e}')
        except ET.ParseError as e:
            raise CommandError(f'Error parsing XML response: {e}')
        except Exception as e:
            raise CommandError(f'An unexpected error occurred: {e}')
