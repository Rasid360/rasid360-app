
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(page_title="راصد 360", layout="wide")

st.title("راصد 360")
st.caption("رصد الانتشار وتحليل التفاعل")

content = st.text_area(
    "أدخل نص المحتوى",
    height=150,
    placeholder="الصق نص المحتوى المنشور هنا..."
)

platforms = {
    "إكس": "x.com",
    "إنستغرام": "instagram.com",
    "تيك توك": "tiktok.com",
    "فيسبوك": "facebook.com"
}

if st.button("ابدأ الرصد", type="primary"):
    if not content.strip():
        st.warning("يرجى إدخال نص المحتوى أولاً.")
    else:
        query = " ".join(content.split()[:12])
        st.info("جاري إعداد البحث عن المحتوى...")

        for platform, domain in platforms.items():
            st.subheader(platform)
            search_url = (
                "https://www.google.com/search?q="
                + quote('site:' + domain + ' "' + query + '"')
            )
            st.markdown(
                f"[عرض نتائج البحث في {platform}]({search_url})"
            )

        st.caption(
            "هذه نسخة تجريبية تستخدم روابط البحث العام. "
            "لا تجمع النتائج أو التفاعلات تلقائياً بعد."
        )
