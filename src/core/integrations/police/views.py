import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import PoliceFoundItem, PoliceLostItem
from .serializers import PoliceFoundItemSerializer, PoliceLostItemSerializer


class PoliceFoundItemsView(View):
    def get(self, request):
        page_no = request.GET.get('pageNo', '1')
        num_of_rows = request.GET.get('numOfRows', '10')

        queryset = PoliceFoundItem.objects.all().order_by('-fdYmd', '-atcId')

        paginator = Paginator(queryset, num_of_rows)

        try:
            items = paginator.page(page_no)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        serializer = PoliceFoundItemSerializer(items, many=True)

        return JsonResponse({
            'status': 'success',
            'data': {
                'items': serializer.data,
                'total': paginator.count,
                'page': int(page_no),
            }
        })


class PoliceLostItemsView(View):
    def get(self, request):
        page_no = request.GET.get('pageNo', '1')
        num_of_rows = request.GET.get('numOfRows', '10')

        queryset = PoliceLostItem.objects.all().order_by('-lstYmd', '-atcId')

        paginator = Paginator(queryset, num_of_rows)

        try:
            items = paginator.page(page_no)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        serializer = PoliceLostItemSerializer(items, many=True)

        return JsonResponse({
            'status': 'success',
            'data': {
                'items': serializer.data,
                'total': paginator.count,
                'page': int(page_no),
            }
        })
