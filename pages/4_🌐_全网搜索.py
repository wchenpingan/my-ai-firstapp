import streamlit as st
from openai import OpenAI
import requests  # 👈 用来发送网络请求

st.set_page_config(page_title="全网搜索 (实时版)", page_icon="🌐")
st.title("🌐 AI 全网搜索助手")

# --- 1. 查票 ---
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ 请先回到 👋 Home 主页输入 DeepSeek API Key！")
    st.stop()
api_key = st.session_state["api_key"]


# --- 2. 真实的搜索函数 (Bocha API) ---
def search_web(query):
    # 👇👇👇 【关键步骤】请在这里填入你刚才申请的 Bocha Key 👇👇👇
    BOCHA_KEY = "sk-2d9cd92113f44898958fa521622546cb"

    if "sk-xxxx" in BOCHA_KEY:
        st.error("❌ 你忘记填入博查的 API Key 了！请去代码里修改。")
        st.stop()

    st.info(f"🔍 正在检索互联网：{query} ...")

    # 构造请求
    url = "https://api.bochaai.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {BOCHA_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "freshness": "noLimit",  # 可以改成 oneDay (一天内), oneWeek (一周内)
        "summary": True,  # 让搜索引擎直接把网页总结好给我们
        "count": 3  # 找前3个结果
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            json_data = response.json()
            # 提取数据
            web_pages = json_data.get("data", {}).get("webPages", {}).get("value", [])

            if not web_pages:
                return "没有找到相关结果。"

            # 把搜到的结果拼成一段话
            context_text = ""
            for idx, page in enumerate(web_pages):
                context_text += f"【来源 {idx + 1}】标题：{page['name']}\n"
                context_text += f"摘要：{page['summary']}\n"
                context_text += f"链接：{page['url']}\n\n"

            return context_text
        else:
            return f"搜索出错：{response.text}"

    except Exception as e:
        return f"网络请求失败：{e}"


# --- 3. 聊天界面 ---
if "search_messages" not in st.session_state:
    st.session_state["search_messages"] = [
        {"role": "assistant", "content": "你好！我是真正的联网 AI。问我今天的新闻、天气或股价吧！"}]

for msg in st.session_state.search_messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("输入你想知道的时事..."):
    # 显示用户问题
    st.session_state.search_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 1. 先去搜索
    web_content = search_web(prompt)

    # 2. 把搜到的东西展示在折叠框里（让用户知道你参考了什么）
    with st.expander("👀 点击查看 AI 参考的搜索结果"):
        st.text(web_content)

    # 3. 拼装 Prompt
    full_prompt = f"""
    用户的问题是：{prompt}

    以下是来自互联网的最新搜索结果：
    {web_content}

    请根据上述搜索结果回答用户的问题。如果搜索结果中没有相关信息，请诚实地告诉用户你不知道。
    """

    # 4. 调用 AI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个基于实时搜索结果的 AI 助手。"},
                {"role": "user", "content": full_prompt}
            ],
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.search_messages.append({"role": "assistant", "content": response})