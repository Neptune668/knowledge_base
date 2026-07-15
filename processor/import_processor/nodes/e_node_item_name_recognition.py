from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeItemNameRecognition(BaseNode):
    """
    主体识别节点：主体识别与标签提取
    """

    name = "node_item_name_recognition"

    def process(self, state: ImportGraphState):
        # 1 参数处理
        file_title,chunks = self._setp_1_get_inputs(state)
        # 2 上下文拼接
        
        # 3 模型识别(总结)

        # 4 回填数据(item_name - > chunks)

        # 5 主体名称向量化（稠密，稀疏）

        # 6 存入milvus向量库

        return state