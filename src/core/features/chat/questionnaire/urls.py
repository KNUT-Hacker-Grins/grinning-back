from django.urls import path
from .views import QuestionnaireApproveAPIView, QuestionnaireDeliverAPIView, ChatbotMessageView 

urlpatterns = [
    path("deliver", QuestionnaireDeliverAPIView.as_view(), name="QuestionnaireDeliverAPIView"),
    path("approve", QuestionnaireApproveAPIView.as_view(), name="QuestionnaireApproveAPIView"),
    path("message", ChatbotMessageView.as_view(), name="ChatbotMessageView"),
]