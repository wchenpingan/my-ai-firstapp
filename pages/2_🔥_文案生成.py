import streamlit as st
from openai import OpenAI

# --- 1. 页面基础设置 ---
st.set_page_config(page_title="爆款文案生成器", page_icon="🔥")
st.title("🔥 爆款文案生成器")

# --- 2. 核心修改：检查“大厅”有没有给钥匙 ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 请先回到 👋 Home 主页输入 API Key！")
    st.stop()  # 如果没有 Key，直接停止运行，不显示后面的内容

# 从全局变量里拿出 Key
api_key = st.session_state["api_key"]

# --- 3. 左侧侧边栏：只留写作参数 (去掉了输入 Key 的地方) ---
with st.sidebar:
    st.header("📝 写作设置")

    # selectbox: 下拉菜单
    platform = st.selectbox("发布平台", ["小红书", "朋友圈", "知乎", "闲鱼"])

    # slider: 滑动条
    creativity = st.slider("创意程度 (越高越疯)", 0.0, 2.0, 1.2)

# --- 4. 主界面：获取输入 ---
topic = st.text_area("请输入你想写的主题或产品特点：", height=100,
                     placeholder="例如：一款不用插电的便携榨汁机，适合露营，粉色外观...")

if st.button("🚀 点击生成文案"):
    if not topic:
        st.warning("请先输入主题！")
        st.stop()

    # --- 5. 核心逻辑：拼装 Prompt ---
    system_prompt = f"""
    你是一个资深的{platform}运营专家。
    请根据用户输入的主题，写一篇吸引眼球的文案。
    要求：
    1. 包含大量Emoji表情。
    2. 语气要{"接地气、生活化" if platform == "朋友圈" else "种草感强、激动"}。
    3. 分段清晰，带有吸引人的标题。
    4. 结尾加上相关的标签(Hashtags)。
    """

    # --- 6. 调用 AI (使用全局 Key) ---
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    with st.spinner("AI 正在疯狂挠头创作中..."):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": topic}
                ],
                temperature=creativity
            )
            result = response.choices[0].message.content

            # --- 7. 展示结果 ---
            st.success("生成成功！")
            st.markdown(result)

        except Exception as e:
            st.error(f"出错了：{e}")