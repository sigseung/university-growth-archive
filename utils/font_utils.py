"""
utils/font_utils.py

Matplotlib과 reportlab(PDF) 둘 다 "한글이 깨지지 않는 폰트"가 필요합니다.
기본 폰트는 한글을 지원하지 않아서 그래프의 한글 라벨이 네모(□)로 깨지고,
PDF에서도 한글이 아예 렌더링되지 않습니다.

이 파일은 OS별로 흔히 설치되어 있는 한글 폰트 경로들을 순서대로 확인해서
'실제로 존재하는 첫 번째 폰트'의 경로를 찾아줍니다. (Windows: 맑은 고딕,
macOS: 애플 고딕, Linux: 나눔고딕/Noto Sans CJK)

★ .ttc(TrueType Collection) 주의사항:
reportlab의 TTFont는 .ttc 파일을 등록은 시켜주지만 실제로는 글리프를
잘못 읽어서, PDF에 한글이 전부 네모(□)로 깨지는 문제가 있습니다.
(직접 겪은 문제라 아래처럼 exclude_collections 옵션으로 명시적으로 걸러냅니다.)
반면 matplotlib은 .ttc를 문제없이 처리하므로, 그래프 쪽은 .ttc를 써도 됩니다.
"""

from pathlib import Path

# 우선순위대로 나열. 위에서부터 확인해서 처음 발견되는 것을 사용합니다.
_CANDIDATE_PATHS = [
    # Windows
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/malgunbd.ttf",
    # macOS
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleGothic.ttf",
    # Linux (Ubuntu 등에 흔히 설치되는 나눔고딕/Noto)
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]

# (경로, exclude_collections였는지) 조합별로 캐싱합니다.
_cache: dict[bool, str | None] = {}


def find_korean_font_path(exclude_collections: bool = False) -> str | None:
    """사용 가능한 한글 폰트 파일 경로를 찾아 반환합니다.
    하나도 없으면 None을 반환하며, 호출하는 쪽에서 '한글이 깨질 수 있다'는
    것을 감안하고 기본 폰트로 폴백해야 합니다.

    exclude_collections=True 이면 .ttc(폰트 컬렉션) 파일은 후보에서 제외합니다.
    reportlab로 PDF를 만들 때는 반드시 True로 호출해야 합니다."""
    if exclude_collections in _cache:
        return _cache[exclude_collections]

    def is_collection(path_str: str) -> bool:
        return path_str.lower().endswith(".ttc")

    for path_str in _CANDIDATE_PATHS:
        if exclude_collections and is_collection(path_str):
            continue
        if Path(path_str).exists():
            _cache[exclude_collections] = path_str
            return path_str

    # matplotlib이 자체적으로 알고 있는 폰트 목록에서도 한 번 더 찾아봅니다.
    try:
        from matplotlib import font_manager

        for font in font_manager.fontManager.ttflist:
            if exclude_collections and is_collection(font.fname):
                continue
            name_lower = font.name.lower()
            if any(k in name_lower for k in ("nanum", "malgun", "noto sans cjk", "applegothic", "gothic")):
                _cache[exclude_collections] = font.fname
                return font.fname
    except Exception:
        pass

    _cache[exclude_collections] = None
    return None
