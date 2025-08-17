from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.features.lostfound.found_items.models import FoundItem

def _compose_text(doc: FoundItem) -> str:
    parts = [doc.title or "", doc.description or "", doc.category or "", doc.color or ""]
    return " ".join(parts)

class FoundItemsRecommander:
    def __init__(self, query: str, top_k: int = 5):
        self.vec = TfidfVectorizer(min_df=1, ngram_range=(1, 2)) 
        self.analy_similarity_for_Tfidf(query, top_k)

    def analy_similarity_for_Tfidf(self, query, top_k) -> List[Dict]:
        items = list(FoundItem.objects.order_by("-created_at")[:2000])  # 최근 2000건에서 추천
        if not items:
            return []
        corpus = [_compose_text(it) for it in items]
        
        X = self.vec.fit_transform(corpus)
        qv = self.vec.transform([query])
        sims = cosine_similarity(qv, X)[0]
        rank = sims.argsort()[::-1][:top_k]
        results = []
        for idx in rank:
            it = items[idx]
            results.append({
                "id": it.id,
                "title": it.title,
                "description": it.description,
                "category": it.category,
                "color": it.color,
                "score": float(sims[idx]),
            })
        return results
