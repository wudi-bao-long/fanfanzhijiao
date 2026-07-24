"""总结服务类： 用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from utils.config_handler import chroma_conf
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


print_runnable = RunnableLambda(print_prompt)


class RagSummarizeService(object):
    SCORE_THRESHOLD = 1.25

    def __init__(self):
        self.vector_store = VectorStoreService()
        self.vector_store.load_document()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self.__init__chain()

    def __init__chain(self):
        chain = self.prompt_template | print_runnable | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        docs_with_scores =self.vector_store.vector_store.similarity_search_with_score(query, k=chroma_conf["k"]
        )
        filtered = []
        for doc, score in docs_with_scores:
            if score < self.SCORE_THRESHOLD:
                filtered.append(doc)
        return filtered

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        if not context_docs:
            return self._not_found_msg()

        result_parts = []
        for i, doc in enumerate(context_docs, 1):
            result_parts.append(f"【结果{i}】{doc.page_content}")

        result = "\n\n".join(result_parts)
        result += f"\n\n---\n以上是知识库检索到的全部{len(context_docs)}家餐厅，每一条数据都是真实存在的。你必须基于以上数据推荐，有多少家就如实推荐多少家，严禁编造任何不在此列表中的餐厅。"
        return result

    def _not_found_msg(self):
        return ("【系统强制约束】知识库中未收录符合该条件的餐厅。""你必须回复用户：""目前知识库还没有这个口味的餐厅，可以换个菜系试试，比如粤菜、川菜、小吃、奶茶。""严禁编造任何不存在的餐厅名或菜名。")


if __name__ == '__main__':
    rag = RagSummarizeService()
    print(rag.rag_summarize("想吃湘菜"))
