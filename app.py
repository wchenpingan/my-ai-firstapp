import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="智能数据分析师", page_icon="📊")
st.title("📊 AI 数据分析师")

with st.sidebar:
    st.header("设置")
    api_key = st.text_input("DeepSeek API Key", type="password")
    st.markdown("---")
    st.info("💡 提示：请上传带有表头的 Excel 或 CSV 文件")

# 1. 文件上传
uploaded_file = st.file_uploader("上传你的表格数据", type=["csv", "xlsx"])

if uploaded_file:
    # 2. 读取数据 (Pandas 是 Python 数据处理的核心库)
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("1. 数据预览")
        st.dataframe(df.head())  # 展示前几行数据

        # 3. 简单的自动化图表
        st.subheader("2. 数据可视化")
        # 找出所有是“数字”的列
        numeric_columns = df.select_dtypes(include=['float', 'int']).columns.tolist()

        if numeric_columns:
            column = st.selectbox("选择要画图的列", numeric_columns)
            st.line_chart(df[column])  # 一键画折线图
        else:
            st.warning("表格里好像没有数字列可以画图？")

        # 4. AI 分析
        st.subheader("3. AI 智能分析")
        if st.button("让 AI 分析数据趋势"):
            if not api_key:
                st.error("请先输入 API Key")
                st.stop()

            # 把数据的前几行转成字符串喂给 AI
            # 注意：真实项目中不能把几万行数据全发给 AI，太贵且会超长。通常只发统计摘要或前N行。
            data_preview = df.head(20).to_string()

            prompt = f"""
            你是一个资深的数据分析师。
            请根据以下表格数据（仅展示了前20行），分析数据的特点、异常值或潜在趋势。
            如果可以看出业务含义，请给出建议。

            数据内容：
            {data_preview}
            """

            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

            with st.spinner("AI 正在看图说话..."):
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"文件读取失败：{e}")