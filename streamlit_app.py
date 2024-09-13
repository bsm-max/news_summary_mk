# pip install feedparser nltk wordcloud matplotlib newspaper3k lxml[html_clean]

import streamlit as st
import feedparser
from newspaper import Article
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# NLTK에서 punkt 데이터 다운로드
def download_nltk_resources():
    nltk.download('punkt')

download_nltk_resources()

# 매일경제 RSS 피드 URL 매핑
RSS_FEEDS = {
    "경제": "https://www.mk.co.kr/rss/30100041/",    # 경제
    "정치": "https://www.mk.co.kr/rss/30200030/",    # 정치
    "사회": "https://www.mk.co.kr/rss/50400012/",    # 사회
    "국제": "https://www.mk.co.kr/rss/30300018/",    # 국제
    "기업경영": "https://www.mk.co.kr/rss/50100032/",  # 기업경영
    "증권": "https://www.mk.co.kr/rss/50200011/",     # 증권
    "부동산": "https://www.mk.co.kr/rss/50300009/",    # 부동산
    "문화연예": "https://www.mk.co.kr/rss/30000023/",  # 문화연예
    "스포츠": "https://www.mk.co.kr/rss/71000001/",    # 스포츠
    "게임": "https://www.mk.co.kr/rss/50700001/"      # 게임
}

# 키워드와 주제를 매칭하는 함수
def classify_topic(keyword):
    keyword = keyword.lower()
    if any(word in keyword for word in ["경제", "금융", "무역", "산업"]):
        return "경제"
    elif any(word in keyword for word in ["정치", "선거", "정부"]):
        return "정치"
    elif any(word in keyword for word in ["사회", "사건", "사고", "복지"]):
        return "사회"
    elif any(word in keyword for word in ["국제", "세계", "외교"]):
        return "국제"
    elif any(word in keyword for word in ["기업", "경영", "사업"]):
        return "기업경영"
    elif any(word in keyword for word in ["증권", "주식", "투자"]):
        return "증권"
    elif any(word in keyword for word in ["부동산", "아파트", "주택"]):
        return "부동산"
    elif any(word in keyword for word in ["문화", "연예", "영화", "음악"]):
        return "문화연예"
    elif any(word in keyword for word in ["스포츠", "축구", "야구"]):
        return "스포츠"
    elif any(word in keyword for word in ["게임", "e스포츠", "비디오 게임"]):
        return "게임"
    return "경제"

# RSS 피드에서 뉴스를 가져오는 함수
def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    return feed['entries']

# 뉴스 기사를 요약하는 함수
def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # 기사 요약 수행
        return article.title, article.summary
    except Exception as e:
        return "기사 요약 불가", f"오류: {str(e)}"

# 워드클라우드 그리기 함수
def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# 메인 함수
def main():
    st.title("뉴스 요약 및 워드클라우드 생성기")
    st.write("관심 있는 키워드를 입력하면 관련 뉴스를 요약하고 워드클라우드를 생성합니다.")
    
    # 사용자 입력 받기
    user_input = st.text_input("관심 있는 주제나 키워드를 입력하세요:")
    
    if user_input:
        # 키워드에 따른 주제 분류
        topic = classify_topic(user_input)
        st.write(f"선택된 주제: {topic}")
    
        # 해당 주제의 RSS 피드 URL 가져오기
        rss_url = RSS_FEEDS.get(topic)
    
        # RSS 피드에서 뉴스 가져오기
        news_items = fetch_rss_feed(rss_url)
    
        if not news_items:
            st.error("RSS 피드에서 뉴스를 가져올 수 없습니다.")
            return
    
        st.write(f"{topic}와 관련된 뉴스 {len(news_items)}개를 가져왔습니다.\n")
    
        # 뉴스 요약 및 워드클라우드를 위한 전체 텍스트 수집
        all_summaries = ""
        for i, news in enumerate(news_items[:10], 1):  # 최대 10개의 뉴스만 처리
            try:
                st.write(f"{i}. [{news.title}]({news.link})")
                # 뉴스 링크에서 기사를 요약합니다.
                title, summary = summarize_article(news.link)
                st.write(f"요약: {summary}")
                all_summaries += " " + summary  # 워드클라우드를 위한 요약문 모음
            except Exception as e:
                st.warning(f"뉴스 {i} 요약 중 오류 발생: {str(e)}\n")
    
        # 워드클라우드 생성 및 출력
        if all_summaries:
            buffer = create_wordcloud(all_summaries)
            plt.figure(figsize=(10, 5))
            plt.imshow(WordCloud(background_color='white').generate(all_summaries), interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
           
            # 워드클라우드 다운로드 버튼 추가
            st.download_button(
                label="워드클라우드 다운로드",
                data=buffer,
                file_name="wordcloud.png",
                mime="image/png"
            )

if __name__ == "__main__":
    main()

