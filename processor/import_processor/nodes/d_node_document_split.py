from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeDocumentSplit(BaseNode):
    """
    文档切分节点：智能文档切片
    """

    name = "node_document_split"

    def process(self, state: ImportGraphState):
        """
                文档切分节点：智能文档切片
                :param state:
                :return:
                """
        # 1 参数处理
        # 2 标题切(初切)
        # 3 无标题兜底(默认标题)
        # 4 块精细化处理(长切短合)
        # 5 打印日志
        # 6 备份
        state["chunks"] = None
        return state
