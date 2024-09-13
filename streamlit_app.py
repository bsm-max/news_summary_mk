import streamlit as st
import feedparser
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import squarify
import re
import matplotlib.font_manager as fm

# 매일경제 RSS 피드 URL 매핑
RSS_FEEDS = {
    "경제": "https://www.mk.co.kr/rss/30100041/",
    "정치": "https://www.mk.co.kr/rss/30200030/",
    "사회": "https://www.mk.co.kr/rss/50400012/",
    "국제": "https://www.mk.co.kr/rss/30300018/",
    "기업경영": "https://www.mk.co.kr/rss/50100032/",
    "증권": "https://www.mk.co.kr/rss/50200011/",
    "부동산": "https://www.mk.co.kr/rss/50300009/",
    "문화연예": "https://www.mk.co.kr/rss/30000023/",
    "스포츠": "https://www.mk.co.kr/rss/71000001/",
    "게임": "https://www.mk.co.kr/rss/50700001/"
}

# 한글 폰트 설정 (예: 맑은 고딕)
def set_korean_font():
    plt.rc('font', family='Malgun Gothic')  # 맑은 고딕 사용
    plt.rc('axes', unicode_minus=False)  # 마이너스 부호가 깨지는 문제 해결

# 키워드와 주제를 매칭하는 함수
def classify_topic(keyword):
    keyword = keyword.lower()
    for category, words in {
        "경제": ["경제", "금융", "무역", "산업"],
        "정치": ["정치", "선거", "정부"],
        "사회": ["사회", "사건", "사고", "복지"],
        "국제": ["국제", "세계", "외교"],
        "기업경영": ["기업", "경영", "사업"],
        "증권": ["증권", "주식", "투자"],
        "부동산": ["부동산", "아파트", "주택"],
        "문화연예": ["문화", "연예", "영화", "음악"],
        "스포츠": ["스포츠", "축구", "야구"],
        "게임": ["게임", "e스포츠", "비디오 게임"]
    }.items():
        if any(word in keyword for word in words):
            return category
    return "경제"

# RSS 피드에서 뉴스를 가져오는 함수
def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    return feed['entries']

# 간단한 요약을 생성하는 함수 (첫 두 문장만 사용)
def simple_summarize(content):
    sentences = content.split('. ')
    return '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else content

# 불필요한 숫자와 특수문자를 제거하는 함수
def clean_text(text):
    # 숫자와 특수기호 제거
    text = re.sub(r'\d+', '', text)  # 모든 숫자 제거
    text = re.sub(r'[^\w\s]', '', text)  # 특수문자 제거
    text = re.sub(r'\b\w{1,2}\b', '', text)  # 1~2글자의 짧은 단어 제거
    return text

# 단어 빈도수를 시각적으로 보여주는 히트맵
def show_word_heatmap(word_counts):
    set_korean_font()  # 한글 폰트 설정
    words, counts = zip(*word_counts)
    heatmap_data = [counts]
    
    plt.figure(figsize=(12, 2))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="coolwarm", xticklabels=words, cbar=False)
    plt.title("단어 빈도수 히트맵")
    plt.show()

# 단어 빈도수를 트리맵으로 시각화하는 함수
def show_word_treemap(word_counts):
    set_korean_font()  # 한글 폰트 설정
    words, counts = zip(*word_counts)
    
    plt.figure(figsize=(10, 6))
    squarify.plot(sizes=counts, label=words, alpha=.8)
    plt.title("단어 빈도수 트리맵")
    plt.axis('off')
    plt.show()

# 메인 함수
def main():
    st.title("뉴스 요약 및 단어 빈도수 시각화")
    user_input = st.text_input("관심 있는 주제나 키워드를 입력하세요:")
    
    # 사용자로부터 표시할 뉴스 개수를 입력받음 (기본값 10개)
    max_news = st.number_input("표시할 뉴스 개수", min_value=1, max_value=50, value=10)
    
    # 뉴스보기 버튼 추가
    if st.button("뉴스보기"):
        if user_input:
            topic = classify_topic(user_input)
            st.write(f"선택된 주제: {topic}")
            
            rss_url = RSS_FEEDS.get(topic)
            news_items = fetch_rss_feed(rss_url)
            
            # 뉴스 개수를 입력한 값만큼 제한하여 가져옴
            selected_news = news_items[:max_news]
            
            if not selected_news:
                st.error("RSS 피드에서 뉴스를 가져올 수 없습니다.")
                return
            
            st.write(f"{topic}와 관련된 뉴스 {len(selected_news)}개를 가져왔습니다.\n")
            
            # 뉴스 요약 및 단어 빈도수를 위한 전체 텍스트 수집
            all_summaries = ""
            for i, news in enumerate(selected_news, 1):
                summary = simple_summarize(news.get("summary", news.get("title", "No content available")))
                st.write(f"{i}. [{news.title}]({news.link})")
                st.write(f"요약: {summary}")
                all_summaries += " " + summary
            
            # 텍스트 전처리 후 단어 빈도 계산
            cleaned_text = clean_text(all_summaries)
            word_counts = Counter(cleaned_text.split()).most_common(10)  # 상위 10개 단어
            
            # 히트맵 시각화
            st.write("### 단어 빈도수 히트맵")
            plt.figure(figsize=(12, 2))
            show_word_heatmap(word_counts)
            st.pyplot(plt)
            
            # 트리맵 시각화
            st.write("### 단어 빈도수 트리맵")
            plt.figure(figsize=(10, 6))
            show_word_treemap(word_counts)
            st.pyplot(plt)

if __name__ == "__main__":
    main()

