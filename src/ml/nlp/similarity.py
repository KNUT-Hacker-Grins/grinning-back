from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.features.lostfound.lost_items.models import LostItem

class LostItemsRecommander:
    def __init__(self, items, query: str, top_k: int = 5):
        self.vec = TfidfVectorizer(min_df=1, ngram_range=(1, 2)) 
        self.analy_similarity_for_Tfidf(items, query, top_k)

    @staticmethod
    def _compose_text(doc: LostItem) -> str:
        parts = [doc.title or "", doc.description or "", doc.category or "", doc.color or ""]
        return " ".join(parts)

    def analy_similarity_for_Tfidf(self, items, query, top_k) -> List[Dict]:
        if not items:
            return []
        corpus = [self._compose_text(it) for it in items]
        
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
