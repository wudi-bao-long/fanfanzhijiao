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
    # ChromaDB 余弦距离阈值：距离越小越相关，>1.0 基本不相关
    SCORE_THRESHOLD = 1.0

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
        # 用带分数的检索，过滤低相关度结果
        docs_with_scores =self.vector_store.vector_store.similarity_search_with_score(
            query, k=chroma_conf["k"]
        )
        filtered = []
        for doc, score in docs_with_scores:
            if score < self.SCORE_THRESHOLD:
                filtered.append(doc)
        return filtered

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        if not context_docs:
            return"抱歉，知识库中暂未收录符合条件的餐厅或菜品，建议换个口味或关键词试试~"

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】：参考资料：{doc.page_content} |参考元数据：{doc.metadata}\n"

        return self.chain.invoke({"input": query, "context": context,})


if __name__ == '__main__':
    rag = RagSummarizeService()
    print(rag.rag_summarize("想吃湘菜"))