import streamlit as st
import database  # 引用管理员

st.set_page_config(page_title="我的 AI 全能工作台", page_icon="👋")

# 初始化数据库
database.create_table()

# --- 检查登录状态 ---
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None  # 默认没登录

# ================================
# 🔒 登录/注册 界面
# ================================
if st.session_state["user_name"] is None:
    st.title("👋 欢迎来到 AI 全能工作台")
    st.info("🔒 请先登录以使用功能")

    # 两个选项卡：登录 / 注册
    tab1, tab2 = st.tabs(["登录", "注册新账号"])

    with tab1:  # 登录页
        username_in = st.text_input("用户名", key="login_user")
        password_in = st.text_input("密码", type="password", key="login_pw")
        if st.button("登录"):
            if database.login_user(username_in, password_in):
                st.session_state["user_name"] = username_in
                st.success("登录成功！")
                st.rerun()  # 刷新网页，进入主界面
            else:
                st.error("用户名或密码错误")

    with tab2:  # 注册页
        new_user = st.text_input("设置用户名", key="reg_user")
        new_pass = st.text_input("设置密码", type="password", key="reg_pw")
        if st.button("注册"):
            if new_user and new_pass:
                if database.register_user(new_user, new_pass):
                    st.success("注册成功！请切换到“登录”标签页进行登录。")
                else:
                    st.error("该用户名已被注册，换一个吧！")
            else:
                st.warning("账号密码不能为空")

    st.stop()  # ⛔ 如果没登录，代码就停在这里，不往下走了

# ================================
# ✅ 登录成功后的主界面
# ================================
st.sidebar.success(f"👤 当前用户: {st.session_state['user_name']}")
if st.sidebar.button("退出登录"):
    st.session_state["user_name"] = None
    st.rerun()

st.title(f"👋 欢迎回来，{st.session_state['user_name']}！")

st.markdown("""
### 这里集成了我开发的所有 AI 工具：
- **💬 智能对话**: 带记忆功能的聊天机器人。
- **🔥 文案生成**: 专为社媒打造的写作助手。
- **📊 数据分析**: 智能文档分析师。
- **🌐 全网搜索**: 实时联网 AI。
""")

st.info("💡 提示：在下方输入一次 API Key，所有工具都能自动使用！")

key = st.text_input("请输入 DeepSeek API Key", type="password")
if key:
    st.session_state["api_key"] = key
    st.success("✅ Key 已保存！")

if "DEEPSEEK_API_KEY" in st.secrets:
    st.session_state["api_key"] = st.secrets["DEEPSEEK_API_KEY"]