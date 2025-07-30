from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, MarianTokenizer, MarianMTModel

LOADED_MODELS = {}

class TranslateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        text = request.data.get("text")
        source = request.data.get("source_language")
        target = request.data.get("target_language")

        if not text or not source or not target:
            return Response({"error": "text, source_language, target_language는 필수입니다."}, status=400)

        if source == target:
            return Response({"error": "source와 target 언어는 서로 달라야 합니다."}, status=400)

        try:
            # en → ko: papago-tako
            if source == "en" and target == "ko":
                model_name = "Helsinki-NLP/opus-mt-tc-big-en-ko"
                if model_name not in LOADED_MODELS:
                    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./hf_models")
                    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir="./hf_models")
                    LOADED_MODELS[model_name] = {"tokenizer": tokenizer, "model": model}
                else:
                    tokenizer = LOADED_MODELS[model_name]["tokenizer"]
                    model = LOADED_MODELS[model_name]["model"]

            # ko → en: helsinki 기본 모델
            elif source == "ko" and target == "en":
                model_name = "Helsinki-NLP/opus-mt-ko-en"
                if model_name not in LOADED_MODELS:
                    tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir="./hf_models")
                    model = MarianMTModel.from_pretrained(model_name, cache_dir="./hf_models")
                    LOADED_MODELS[model_name] = {"tokenizer": tokenizer, "model": model}
                else:
                    tokenizer = LOADED_MODELS[model_name]["tokenizer"]
                    model = LOADED_MODELS[model_name]["model"]

            else:
                return Response({"error": "지원 언어쌍은 en→ko, ko→en 뿐입니다."}, status=400)

            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            if 'token_type_ids' in inputs:
                inputs.pop('token_type_ids')
            # generate() 개선된 파라미터
            output_ids = model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                no_repeat_ngram_size=3,
                repetition_penalty=2.5,
                length_penalty=1.0,
                early_stopping=True
            )

            translated = tokenizer.decode(output_ids[0], skip_special_tokens=True)

            return Response({
                "original": text,
                "translated": translated,
                "source_language": source,
                "target_language": target
            })
        except Exception as e:
            return Response({"error": f"번역 중 오류 발생: {str(e)}"}, status=500)
