# pip install feedparser nltk wordcloud matplotlib newspaper3k lxml[html_clean]

import streamlit as st
import feedparser
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from io import BytesIO
import re

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

# 워드클라우드 생성 함수
def create_wordcloud(text):
    stopwords = set(STOPWORDS)
    # 추가 불용어 설정: 의미 없는 단어나 숫자와 관련된 불필요한 단어들
    stopwords.update(["said", "news", "reuters", "기사", "요약", "뉴스", "ai", "year", "month", "day", "week", "one", "two", "three", "million", "billion", "trillion", "dollar"])

    # 텍스트 정리 후 워드클라우드 생성
    cleaned_text = clean_text(text)
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(cleaned_text)
    
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# 메인 함수
def main():
    st.title("뉴스 요약 및 워드클라우드 생성기")
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
            
            # 뉴스 요약 및 워드클라우드를 위한 전체 텍스트 수집
            all_summaries = ""
            for i, news in enumerate(selected_news, 1):
                summary = simple_summarize(news.get("summary", news.get("title", "No content available")))
                st.write(f"{i}. [{news.title}]({news.link})")
                st.write(f"요약: {summary}")
                all_summaries += " " + summary
            
            # 워드클라우드 생성 및 출력
            if all_summaries:
                buffer = create_wordcloud(all_summaries)
                plt.figure(figsize=(10, 5))
                plt.imshow(WordCloud(background_color='white').generate(all_summaries), interpolation='bilinear')
                plt.axis('off')
                st.pyplot(plt)
                st.download_button("워드클라우드 다운로드", buffer, "wordcloud.png", "image/png")

if __name__ == "__main__":
    main()

