import os
from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st

if "DASHSCOPE_API_KEY" in st.secrets:
    os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]
import time

from agent.react_agent import ReactAgent

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="饭饭之交",
    page_icon="🍜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==================== 自定义样式 ====================
st.markdown("""
<style>
    /* 隐藏 Streamlit 默认顶栏 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* 整体背景 */
    .stApp {
        background: linear-gradient(180deg, #fff8f0 0%, #ffffff 100%);
    }

    /* 标题区域 */
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ff6b35, #f7c948);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        font-size: 1rem;
        color: #999;
        margin-bottom: 1.5rem;
    }

    /* 随机按钮 */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #ff6b35, #f7c948) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
        margin-top: 0.3rem;
    }
    div[data-testid="stButton"] button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }

    /* 聊天输入框 */
    div[data-testid="stChatInput"] textarea {
        border-radius: 20px !important;
        border: 2px solid #ffe0cc !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 8px rgba(255, 107, 53, 0.2) !important;
    }

    /* 用户消息气泡 */
    div[data-testid="stChatMessage"]:has(.stChatMessageAvatarUser) {
        background: linear-gradient(135deg, #ff6b35, #f7c948);
        border-radius: 18px 18px 4px 18px;
        padding: 0.8rem 1.2rem;
        color: white;
    }

    /* AI 消息气泡 */
    div[data-testid="stChatMessage"]:has(.stChatMessageAvatarAssistant) {
        background: #fff;
        border: 1px solid #ffe0cc;
        border-radius: 18px 18px 18px 4px;
        padding: 0.8rem 1.2rem;
        color: #333;
    }

    /* 分割线 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffe0cc, transparent);
    }
</style>
""", unsafe_allow_html=True)

# ==================== 头部 ====================
st.markdown('<div class="main-title">🍜 饭饭之交</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">不知道吃什么？问我，你的赛博饭搭子</div>',
unsafe_allow_html=True)
st.divider()

# ==================== Agent 初始化 ====================
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("### 🌤️ 关于饭饭之交")
    st.caption("基于你的口味、预算和实时天气，从湛江校园周边美食中智能推荐。")
    st.divider()
    st.caption("💡 试试这些：")
    st.caption("• 推荐个好吃的，预算15块")
    st.caption("• 想吃辣的，离南门近的")
    st.caption("• 下雨天吃什么方便")

# ==================== 聊天历史 ====================
for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ==================== 输入区域 ====================
col_input, col_btn = st.columns([4, 1])
with col_input:
    prompt = st.chat_input(placeholder="跟我说说你的口味、预算，帮你找好吃的...")
with col_btn:
    random_clicked = st.button("🎲 不知道吃啥")

if random_clicked:
    prompt = "我今天不知道吃什么，请帮我从知识库里随机推荐一款食物，要有惊喜感！推荐完后告诉我湛江今天的天气适不适合走远路。"

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("🔍 饭饭之交帮你找好吃的..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

    with st.chat_message("assistant"):
        full_response = st.write_stream(capture(res_stream, response_messages))
    st.session_state["message"].append({"role": "assistant", "content":
response_messages[-1]})
    st.rerun()