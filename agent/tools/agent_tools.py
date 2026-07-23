import requests
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path
import random

rag = RagSummarizeService()


# ==================== 知识库检索（保留，核心功能） ====================

@tool(description="从美食知识库中检索餐厅和菜品信息，根据用户的口味、预算、位置等条件搜索推荐")


def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

# ==================== 真实天气（重写，调用 Open-Meteo 免费 API）


WEATHER_CODE_MAP = {
    0: "晴天", 1: "大部晴朗", 2: "多云", 3: "阴天",
    45: "有雾", 48: "雾凇",
    51: "小雨", 53: "中雨", 55: "大雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "中阵雨", 82: "大阵雨",
    95: "雷暴", 96: "冰雹雷暴", 99: "强冰雹雷暴",
}


@tool(description="获取指定城市的实时天气信息，返回天气状况、温度、湿度、风速")
def get_weather(city: str) -> str:
    try:
        # 第一步：城市名 → 经纬度
        geo_url =f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh"
        geo_resp = requests.get(geo_url, timeout=10).json()

        if not geo_resp.get("results"):
            return f"没找到「{city}」的天气信息，换个城市名试试？"

        result = geo_resp["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        city_name = result.get("name", city)

# 第二步：经纬度 → 实时天气
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code")
        weather_resp = requests.get(weather_url, timeout=10).json()
        current = weather_resp["current"]

        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]

        weather_desc = WEATHER_CODE_MAP.get(code, f"未知天气(code={code})")

        return (
        f"城市{city_name}当前天气：{weather_desc}，"
        f"气温{temp}°C，空气湿度{humidity}%，风速{wind}km/h")

    except Exception as e:
        return f"获取天气失败：{type(e).__name__} - {e}"

# ==================== 用户位置（保留，返回默认城市供天气查询用）


@tool(description="获取用户所在的城市名称，以字符串形式返回")
def get_user_location() -> str:
    return "Zhanjiang"

# ==================== 随机推荐（新增，从知识库随机抽一条） ====================

@tool(description="从美食知识库中随机推荐一款食物或餐厅，用于用户不知道吃什么时使用")
def random_food() -> str:
    try:
        import chromadb

        chroma_path = get_abs_path(chroma_conf["persist_directory"])
        collection_name = chroma_conf["collection_name"]

        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_or_create_collection(name=collection_name)

        count = collection.count()
        if count == 0:
            return "知识库还是空的，暂时没法随机推荐。试试直接告诉我你的口味偏好~"

        offset = random.randint(0, count - 1)
        result = collection.get(limit=1, offset=offset, include=["documents"])

        if result["documents"]:
            content = result["documents"][0]
            return f"为你随机挑选了一款：\n{content}"

        return "随机推荐没抽到结果，试试直接告诉我你的口味偏好~"

    except Exception as e:
        return f"随机推荐暂时不可用：{type(e).__name__} - {e}"