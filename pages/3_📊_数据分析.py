import streamlit as st
import pandas as pd
from openai import OpenAI
import pdfplumber

st.set_page_config(page_title="智能数据分析师", page_icon="📊")
st.title("📊 智能数据分析师")

if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 请先回到 👋 Home 主页输入 API Key！")
    st.stop()

api_key = st.session_state["api_key"]

st.info("💡 支持上传 CSV、Excel 表格或 PDF 文档")
uploaded_file = st.file_uploader("请拖入文件", type=["csv", "xlsx", "pdf"])

if uploaded_file:
    if uploaded_file.name.endswith('.pdf'):
        st.subheader("📄 PDF 内容分析")
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                all_text = ""
                for page in pdf.pages[:5]:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
            
            if not all_text:
                st.warning("这好像是纯图片 PDF，我读不到文字 😭")
                st.stop()
                
            with st.expander("👀 点击查看提取的文字"):
                st.text(all_text[:1000] + "...") 

            if st.button("🤖 让 AI 总结文档"):
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                prompt = f"请阅读以下文档内容，并总结核心观点：\n\n{all_text[:3000]}"
                
                with st.spinner("AI 正在阅读中..."):
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        stream=True
                    )
                    st.write_stream(stream)

        except Exception as e:
            st.error(f"解析 PDF 失败: {e}")

    else:
        st.subheader("📊 表格数据分析")
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("数据预览（前 5 行）：")
            st.dataframe(df.head())

            numeric_cols = df.select_dtypes(include=['float', 'int']).columns
            if len(numeric_cols) > 0:
                col_to_plot = st.selectbox("选择要画图的列", numeric_cols)
                st.line_chart(df[col_to_plot])
            
            if st.button("🤖 让 AI 分析数据趋势"):
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                data_str = df.head(10).to_string()
                prompt = f"请分析以下数据趋势：\n{data_str}"
                
                with st.spinner("AI 正在看图说话..."):
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        stream=True
                    )
                    st.write_stream(stream)

        except Exception as e:
            st.error(f"表格读取失败: {e}")
