from django.urls import path
from .views import ReportCreateView, ReportListView, MarkAsFoundView

urlpatterns = [
    path('posts/<int:post_id>/report', ReportCreateView.as_view(), name='report_post'),
    path('admin/reports', ReportListView.as_view(), name='report_list'),
    path('lost-items/<int:id>/found', MarkAsFoundView.as_view(), name='found_lost_item')
]