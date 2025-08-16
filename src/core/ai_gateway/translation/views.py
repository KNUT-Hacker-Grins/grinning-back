from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ml.nlp.translator import translate_text

class TranslateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        text = request.data.get("text")
        source = request.data.get("source_language")
        target = request.data.get("target_language")

        # 원래의 입력 검증/에러 메시지와 동일한 동작
        if not text or not source or not target:
            return Response({"error": "text, source_language, target_language는 필수입니다."}, status=400)

        if source == target:
            return Response({"error": "source와 target 언어는 서로 달라야 합니다."}, status=400)

        try:
            translated = translate_text(text=text, source=source, target=target)
            return Response({
                "original": text,
                "translated": translated,
                "source_language": source,
                "target_language": target
            })
        except ValueError as ve:
            # 지원 언어쌍 오류 등 로직상 400이어야 하는 케이스
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            return Response({"error": f"번역 중 오류 발생: {str(e)}"}, status=500)