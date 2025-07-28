from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# 요청이 들어올 때 로딩 (캐시 덮어쓰기 문제 방지)
LOADED_MODELS = {}

class TranslateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # transformers 임포트를 메서드 내부로 이동
        from transformers import MarianMTModel, MarianTokenizer 

        text = request.data.get("text")
        source = request.data.get("source_language")
        target = request.data.get("target_language")

        if not text or not source or not target:
            return Response({"error": "text, source_language, target_language는 필수입니다."}, status=400)

        lang_pair = f"{source}-{target}"
        if lang_pair not in ["ko-en", "en-ko"]:
            return Response({"error": "지원 언어는 'ko-en', 'en-ko' 만 가능합니다."}, status=400)

        try:
            if lang_pair not in LOADED_MODELS:
                model = MarianMTModel.from_pretrained(
                    f"Helsinki-NLP/opus-mt-{lang_pair}",
                    cache_dir="/tmp/hf_models" # Render 환경에 맞게 캐시 디렉토리 변경
                )
                tokenizer = MarianTokenizer.from_pretrained(
                    f"Helsinki-NLP/opus-mt-{lang_pair}",
                    cache_dir="/tmp/hf_models" # Render 환경에 맞게 캐시 디렉토리 변경
                )
                LOADED_MODELS[lang_pair] = {"model": model, "tokenizer": tokenizer}
            else:
                model = LOADED_MODELS[lang_pair]["model"]
                tokenizer = LOADED_MODELS[lang_pair]["tokenizer"]

            inputs = tokenizer.encode(text, return_tensors="pt", truncation=True)
            outputs = model.generate(inputs, max_length=128)
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return Response({
                "original": text,
                "translated": translated_text,
                "source_language": source,
                "target_language": target
            })

        except Exception as e:
            return Response({"error": f"번역 중 오류 발생: {str(e)}"}, status=500)