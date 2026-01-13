import streamlit as st
from PIL import Image
import base64
from zhipuai import ZhipuAI  # 👈 引入国产大模型库

st.set_page_config(page_title="AI 视觉分析", page_icon="📷")
st.title("📷 AI 视觉分析助手 (智谱 GLM-4V 版)")

# --- 1. 登录校验 ---
if "user_name" not in st.session_state or st.session_state["user_name"] is None:
    st.warning("🔒 请先在 👋 Home 主页登录账号！")
    st.stop()


# --- 2. 核心函数：把图片变成字符串 (简历考点!) ---
def image_to_base64(image_file):
    """
    将 Streamlit 的上传文件对象转换为 Base64 字符串
    """
    # 1. 拿到文件的二进制数据
    # getvalue() 是 BytesIO 对象的方法，能直接拿到内存里的 0101 数据
    img_bytes = image_file.getvalue()

    # 2. 编码成 Base64
    encoded_string = base64.b64encode(img_bytes).decode('utf-8')
    return encoded_string


# --- 3. 界面逻辑 ---
st.info("💡 请拍摄或上传一张照片，智谱 AI 将为你分析内容。")

# 获取图片 (兼容拍照和上传)
camera_photo = st.camera_input("点击拍照")
uploaded_photo = st.file_uploader("或者上传本地图片", type=["jpg", "jpeg", "png"])

image_to_analyze = camera_photo if camera_photo else uploaded_photo

if image_to_analyze:
    st.markdown("---")
    st.subheader("🖼️ 图片预览")

    # 展示图片
    try:
        img_pil = Image.open(image_to_analyze)
        st.image(img_pil, caption="待分析图片", use_column_width=True)
    except Exception as e:
        st.error("图片文件损坏")
        st.stop()

    # --- 4. AI 分析部分 ---
    st.subheader("🤖 AI 分析结果")

    # 这一步可以做成让用户选，比如“分析物体”、“提取文字”、“写首诗”
    prompt_text = st.text_input("你想让 AI 看图说什么？",
                                value="请详细描述这张图片里的内容，如果里面有文字，请帮我提取出来。")

    if st.button("🚀 开始识别"):
        # 👇 填入你的智谱 Key
        ZHIPU_API_KEY = "59e71d7bfc2f4779afc4c33b43becbbf.Ow5PwWQ0ZOqeFS1O"

        if "xxx" in ZHIPU_API_KEY:
            st.error("❌ 别忘了填入你的智谱 API Key！")
            st.stop()

        client = ZhipuAI(api_key=ZHIPU_API_KEY)

        with st.spinner("正在将图片编码并发送给云端大脑..."):
            try:
                base64_str = image_to_base64(image_to_analyze)

                response = client.chat.completions.create(
                    model="glm-4v-plus",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}}
                            ]
                        }
                    ],
                    stream=True
                )


                # 👇👇👇【修复的核心代码】👇👇👇
                # 我们写一个简单的生成器函数，专门用来“剥壳”，只取出 content 里的文字
                def stream_parser(stream_response):
                    for chunk in stream_response:
                        # 检查包裹里有没有货
                        if chunk.choices and chunk.choices[0].delta.content:
                            # 有货就 yield (产出) 里面的文字
                            yield chunk.choices[0].delta.content


                # 把“剥壳”后的干净文字流喂给 Streamlit
                st.write_stream(stream_parser(response))
                # 👆👆👆 修复结束 👆👆👆

                st.success("✅ 分析完成！")

            except Exception as e:
                st.error(f"分析失败：{e}")