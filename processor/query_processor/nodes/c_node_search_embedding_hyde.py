import json

from config.milvus_config import milvus_config
from processor.query_processor.base import NodeBase
from processor.query_processor.prompt.search_embedding_hyde import HYDE_PROMPT
from processor.query_processor.state import QueryGraphState
from tool.logger import logger
from utils.embedding_utils import generate_embeddings
from utils.llm_utils import get_llm_client
from utils.milvus_utils import get_milvus_client, create_hybrid_search_requests, hybrid_search


class NodeSearchEmbeddingHyde(NodeBase):
    """
    节点功能：HyDE (Hypothetical Document Embedding)
    先让 LLM 生成假设性答案，再对答案进行向量检索，提高召回率。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_search_embedding_hyde"

    def process(self, state: QueryGraphState) -> QueryGraphState:
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        logger.info(f"【{self.name}】节点逻辑")
        # 1 参数处理
        item_names = state.get("item_names")  # 命中设备名
        rewritten_query = state.get("rewritten_query")  # 语义搜索条件

        # 2 大模型生成假设性文档
        hyde_doc = self._step_1_create_embedding_hyde_doc(rewritten_query)
        print(f"假设性回答：{hyde_doc}")

        # 3 用"重写问题+假设性文档"搜索文本块
        response = self._setp_2_search_embedding_hyde(
            rewritten_query=rewritten_query,
            hyde_doc=hyde_doc,
            item_names=item_names
        )

        # 4 结果解析
        # json_response = json.dumps(response, ensure_ascii=False, indent=4)
        print(f"response[0]：{response[0]}")
        # return state
        return {"hyde_embedding_chunks": response[0] if response else [], "hyde_doc": hyde_doc}

