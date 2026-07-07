from django.urls import path
from .views import QuestionnaireApproveAPIView, QuestionnaireDeliverAPIView, QuestionHealthView, QuestionMessageView

urlpatterns = [
    path("deliver", QuestionnaireDeliverAPIView.as_view(), name="QuestionnaireDeliverAPIView"),
    path("approve", QuestionnaireApproveAPIView.as_view(), name="QuestionnaireApproveAPIView"),
    path("message", QuestionMessageView.as_view(), name="QuestionMessageView"),
    path('health', QuestionHealthView.as_view(), name='QuestionHealthView'),
]