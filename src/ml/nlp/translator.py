from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    MarianTokenizer,
    MarianMTModel,
)

# 기존과 동일한 전역 캐시
LOADED_MODELS = {}

def translate_text(text: str, source: str, target: str) -> str:
    """
    기존 TranslateAPIView 안에 있던 로직을 그대로 옮김.
    반환값은 '번역된 텍스트' 문자열 하나(동작 동일).
    """
    if not text or not source or not target:
        raise ValueError("text, source_language, target_language는 필수입니다.")

    if source == target:
        raise ValueError("source와 target 언어는 서로 달라야 합니다.")

    # en → ko
    if source == "en" and target == "ko":
        model_name = "Helsinki-NLP/opus-mt-tc-big-en-ko"
        if model_name not in LOADED_MODELS:
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./hf_models")
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir="./hf_models")
            LOADED_MODELS[model_name] = {"tokenizer": tokenizer, "model": model}
        else:
            tokenizer = LOADED_MODELS[model_name]["tokenizer"]
            model = LOADED_MODELS[model_name]["model"]

    # ko → en
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
        # 원래 API에서 400을 내던 부분은 View에서 처리하므로 여기선 예외로 전달
        raise ValueError("지원 언어쌍은 en→ko, ko→en 뿐입니다.")

    # 원문 코드 그대로
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    if 'token_type_ids' in inputs:
        inputs.pop('token_type_ids')

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
    return translated