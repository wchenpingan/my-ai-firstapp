import streamlit as st
from openai import OpenAI
import database  # 导入管理员

st.title("💬 智能对话助手 (私密版)")

# --- 1. 安检：必须登录才能进 ---
if "user_name" not in st.session_state or st.session_state["user_name"] is None:
    st.warning("🔒 请先在 👋 Home 主页登录账号！")
    st.stop()  # ⛔ 没登录就停车

# 获取当前是谁在登录
current_user = st.session_state["user_name"]

# --- 2. 检查 Key ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 请先回到 👋 Home 主页输入 API Key！")
    st.stop()
api_key = st.session_state["api_key"]

# --- 3. 初始化数据库 (以防万一) ---
database.create_table()

# --- 4. 加载历史记录 (关键修改！) ---
if "messages" not in st.session_state:
    # 👇【核心改动】查账时，带上 current_user (用户名)
    db_history = database.get_history(current_user)

    if db_history:
        st.session_state["messages"] = db_history
    else:
        st.session_state["messages"] = [{"role": "assistant", "content": f"你好 {current_user}！我是你的专属 AI 助手。"}]

# 显示历史消息
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 5. 处理新消息 ---
if prompt := st.chat_input():
    # A. 用户说话
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 👇【核心改动】存档时，也要带上 current_user
    database.add_message(current_user, "user", prompt)

    # B. AI 回复
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # 👇【核心改动】AI 的话存档也要带上 current_user
    database.add_message(current_user, "assistant", response)