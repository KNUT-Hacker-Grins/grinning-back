class ImageClassificationError(Exception):
    def __init__(self, message="이미지 분류에 실패했습니다"):
        super().__init__(message)