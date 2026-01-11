import streamlit as st
from openai import OpenAI

st.title("💬 智能对话助手")

# --- 1. 检查 Key (和刚才一样) ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 请先回到 👋 Home 主页输入 API Key！")
    st.stop()

api_key = st.session_state["api_key"]

# --- 2. 初始化历史记录 (和刚才一样) ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是你的 AI 助手，有什么可以帮你的吗？"}]

# 显示历史消息
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 3. 处理新消息 (核心变化在这里！) ---
if prompt := st.chat_input():
    # 3.1 显示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3.2 调用 AI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # [新知识点] stream=True: 告诉 AI "想出一个字就发给我一个字，别等全部想完"
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=st.session_state.messages,
        stream=True
    )

    # 3.3 实时显示 (流式输出)
    with st.chat_message("assistant"):
        # st.write_stream 是 Streamlit 专门用来处理流式数据的神器
        # 它会自动处理那些碎片的文字，把它拼成流畅的打字机效果
        response = st.write_stream(stream)

    # 3.4 把完整的回复存入历史 (这样下次刷新还在)
    st.session_state.messages.append({"role": "assistant", "content": response})