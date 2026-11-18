
import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

st.set_page_config(
    page_title="راصد 360",
    page_icon="📊",
    layout="wide"
)

st.title("راصد 360")
st.caption("رصد انتشار الرسائل التوعوية وتحليل التفاعل عبر المنصات")

if "results" not in st.session_state:
    st.session_state.results = []

st.header("الرسالة الأصلية")

original_url = st.text_input(
    "رابط المنشور الأصلي",
    value="https://x.com/ssd_gov_ae/status/2122555485698273370"
)

original_text = st.text_area(
    "نص الرسالة التوعوية",
    height=140
)

st.header("البحث عبر المنصات")

keywords = st.text_input(
    "كلمات البحث",
    value="الأفكار المتطرفة رسائل تحريضية الكراهية العنف"
)

q = quote(keywords)

search_links = {
    "إكس": f"https://x.com/search?q={q}&f=live",
    "إنستغرام": f"https://www.google.com/search?q=site%3Ainstagram.com+{q}",
    "تيك توك": f"https://www.tiktok.com/search?q={q}",
    "فيسبوك": f"https://www.facebook.com/search/posts/?q={q}"
}

for platform, link in search_links.items():
    st.link_button(
        f"البحث في {platform}",
        link,
        use_container_width=True
    )

st.info(
    "هذه روابط بحث موجّه. لا يجمع التطبيق جميع نتائج المنصات تلقائيًا."
)

st.header("إضافة نتائج موثقة")

with st.form("result_form", clear_on_submit=True):
    platform = st.selectbox(
        "المنصة",
        ["إكس", "إنستغرام", "تيك توك", "فيسبوك"]
    )

    account = st.text_input("الحساب الناشر")
    post_url = st.text_input("رابط المنشور")
    post_text = st.text_area("نص المنشور المكتشف")

    likes = st.number_input(
        "الإعجابات", min_value=0, value=0
    )
    comments = st.number_input(
        "التعليقات", min_value=0, value=0
    )
    shares = st.number_input(
        "المشاركات", min_value=0, value=0
    )
    views = st.number_input(
        "المشاهدات", min_value=0, value=0
    )

    top_reply = st.text_area("أبرز تعليق متاح")

    add = st.form_submit_button("إضافة النتيجة")

    if add:
        if not post_url.strip():
            st.error("يجب إدخال رابط المنشور.")
        else:
            st.session_state.results.append({
                "المنصة": platform,
                "الحساب": account,
                "الرابط": post_url,
                "النص": post_text,
                "الإعجابات": likes,
                "التعليقات": comments,
                "المشاركات": shares,
                "المشاهدات": views,
                "أبرز رد": top_reply
            })
            st.success("تمت إضافة النتيجة.")

st.header("استيراد بيانات النتائج")

uploaded = st.file_uploader(
    "رفع ملف CSV للنتائج الموثقة",
    type=["csv"]
)

df = pd.DataFrame(st.session_state.results)

if uploaded is not None:
    try:
        imported = pd.read_csv(uploaded)
        df = pd.concat(
            [df, imported],
            ignore_index=True
        )
        st.success("تمت قراءة الملف.")
    except Exception as error:
        st.error(f"تعذر قراءة الملف: {error}")

st.header("لوحة التحليل")

if df.empty:
    st.warning(
        "لا توجد نتائج موثقة بعد. "
        "لا يمكن تحديد حجم الانتشار أو اتجاه التفاعل دون بيانات."
    )
else:
    numeric_cols = [
        "الإعجابات",
        "التعليقات",
        "المشاركات",
        "المشاهدات"
    ]

    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    df["إجمالي التفاعل"] = (
        df["الإعجابات"]
        + df["التعليقات"]
        + df["المشاركات"]
    )

    total_posts = len(df)
    total_engagement = int(df["إجمالي التفاعل"].sum())
    total_views = int(df["المشاهدات"].sum())

    c1, c2, c3 = st.columns(3)

    c1.metric("المنشورات المرصودة", total_posts)
    c2.metric("التفاعلات المرصودة", f"{total_engagement:,}")
    c3.metric("المشاهدات المسجلة", f"{total_views:,}")

    st.subheader("أكثر المنصات تفاعلًا")

    summary = (
        df.groupby("المنصة", dropna=False)
        .agg(
            المنشورات=("الرابط", "count"),
            التفاعلات=("إجمالي التفاعل", "sum"),
            المشاهدات=("المشاهدات", "sum")
        )
        .sort_values("التفاعلات", ascending=False)
    )

    st.dataframe(summary, use_container_width=True)
    st.bar_chart(summary["التفاعلات"])

    st.caption(
        "الترتيب يعتمد على النتائج المسجلة فقط، "
        "وليس على جميع منشورات الإنترنت."
    )

    st.subheader("تحليل اتجاه التعليقات")

    positive_words = [
        "ممتاز", "شكرا", "شكراً", "أحسنت",
        "مفيد", "ندعم", "صحيح", "مهم"
    ]

    negative_words = [
        "سيئ", "كذب", "خطأ", "فاشل",
        "مضلل", "رفض", "غير صحيح"
    ]

    def sentiment(text):
        if not isinstance(text, str) or not text.strip():
            return "غير متاح"

        positive = sum(
            word in text for word in positive_words
        )
        negative = sum(
            word in text for word in negative_words
        )

        if positive > negative:
            return "إيجابي مبدئيًا"
        elif negative > positive:
            return "سلبي مبدئيًا"
        else:
            return "محايد أو غير محسوم"

    if "أبرز رد" not in df.columns:
        df["أبرز رد"] = ""

    df["اتجاه الرد"] = df["أبرز رد"].apply(sentiment)

    replies = df[
        df["أبرز رد"].fillna("").astype(str).str.strip() != ""
    ]

    st.subheader("أبرز الردود")

    if replies.empty:
        st.info("لا توجد ردود متاحة للتحليل.")
    else:
        st.dataframe(
            replies[
                ["المنصة", "أبرز رد", "اتجاه الرد", "الرابط"]
            ],
            use_container_width=True
        )

    st.caption(
        "تحليل المشاعر هنا أولي ويعتمد على كلمات دالة، "
        "وليس نموذج ذكاء اصطناعي متقدمًا."
    )

    st.subheader("جميع الأدلة")

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "تنزيل النتائج CSV",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="rasid360_results.csv",
        mime="text/csv"
    )

st.header("التقرير التفصيلي")

report = [
    "راصد 360 - تقرير متابعة الانتشار والتفاعل",
    f"تاريخ التقرير: {datetime.now():%Y-%m-%d %H:%M}",
    f"رابط المنشور الأصلي: {original_url}",
    f"نص الرسالة: {original_text}",
    "",
    "المنهجية:",
    "بحث موجّه وتوثيق النتائج المتاحة عبر المنصات.",
    "التغطية ليست شاملة أو آلية بالكامل.",
    ""
]

if df.empty:
    report.append("لا توجد نتائج خارجية موثقة بعد.")
else:
    report.extend([
        f"عدد المنشورات: {total_posts}",
        f"إجمالي التفاعل: {total_engagement:,}",
        f"المشاهدات المسجلة: {total_views:,}",
        "",
        "مقارنة المنصات:"
    ])

    for platform, row in summary.iterrows():
        report.append(
            f"{platform}: "
            f"{int(row['المنشورات'])} منشورات، "
            f"{int(row['التفاعلات'])} تفاعلات"
        )

    report.extend(["", "أبرز الردود:"])

    if replies.empty:
        report.append("لا توجد ردود موثقة.")
    else:
        for _, row in replies.head(10).iterrows():
            report.append(
                f"{row['المنصة']}: "
                f"{row['أبرز رد']} "
                f"({row['اتجاه الرد']})"
            )

    report.extend([
        "",
        "ملاحظة منهجية:",
        "الأرقام تمثل النتائج المتاحة فقط.",
        "وتصنيف اتجاه التعليقات تقديري ويحتاج مراجعة."
    ])

report_text = "\n".join(report)

st.text_area(
    "معاينة التقرير",
    report_text,
    height=350
)

st.download_button(
    "تنزيل التقرير",
    report_text.encode("utf-8-sig"),
    file_name="rasid360_report.txt",
    mime="text/plain"
)

st.warning(
    "لا تدخلي بيانات سرية في التطبيق العام. "
    "النتائج المضافة لا تُحفظ في قاعدة بيانات دائمة."
)
