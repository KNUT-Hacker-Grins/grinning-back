import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.features.lostfound.lost_items.models import LostItem


class LostItemsRecommander:
    def __init__(self, total_count: int | None = None):
        # 한글 대응: 문자 n-gram으로 변경
        self.vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=1)
        self.total_count = int(total_count) if total_count else 2000

    @staticmethod
    def _compose_text(doc: LostItem) -> str:
        category = doc.category
        if isinstance(category, list):
            category = " ".join(map(str, category))

        parts = [
            doc.title or "", 
            doc.description or "", 
            str(category) or "", 
            doc.color or ""
        ]
        return " ".join(filter(None, parts))

    def analy_similarity_for_Tfidf(self, query: str, top_k: int = 5):
        # 최신순 일부만 로드 후 리스트화(인덱싱 안전)
        qs = LostItem.objects.all().order_by("-created_at")[: self.total_count]
        items = list(qs)
        if not items:
            return []

        corpus = [self._compose_text(it) for it in items]
        X = self.vec.fit_transform(corpus)

        # 쿼리 벡터
        qv = self.vec.transform([query])
        if qv.nnz == 0:
            # 쿼리 전처리 결과가 전부 OOV -> 의미 있는 비교 불가
            return []

        sims = cosine_similarity(qv, X).ravel()
        if sims.size == 0 or float(np.max(sims)) <= 0.0:
            # 전부 0점이면 추천 의미 없음
            return []

        # 상위 k개 인덱스 추출 (k > n 문제 방지)
        k = min(top_k, len(items))
        top_idx = np.argpartition(sims, -k)[-k:]          # 상위 k개 비정렬
        top_idx = top_idx[np.argsort(sims[top_idx])[::-1]]  # 점수 기준 내림차순 정렬

        results = []
        for idx in top_idx:
            it = items[int(idx)]
            results.append({
                "id": it.id,
                "title": it.title,
                "description": it.description,
                "category": it.category,
                "color": it.color,
                "score": float(sims[int(idx)]),
            })
        return results
