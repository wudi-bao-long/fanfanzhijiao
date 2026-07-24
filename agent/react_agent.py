from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import rag_summarize, random_food
from agent.tools.middleware import monitor_tool, log_before_model
from langchain_core.messages import AIMessage


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, random_food],
            middleware=[monitor_tool, log_before_model],
        )

    def execute_stream(self, query: str, history: list = None):
        messages = []
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        input_dict = {"messages": messages}

        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            latest_message = chunk["messages"][-1]
            # 只输出最终回复（AIMessage且没有tool_calls），过滤掉思考过程和工具调用
            if isinstance(latest_message, AIMessage) and not latest_message.tool_calls:
                if latest_message.content:
                    yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("帮我随机推荐一道菜"):
        print(chunk, end="", flush=True)