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
        content, file_title = self._step_1_get_inputs(state)

        # 2 标题切(初切)
        sections, title_count, lines_count = self._step_2_split_by_title(content, file_title)

        # 3 无标题兜底(默认标题)
        sections = self._step_3_handle_no_title(content, sections, title_count, file_title)

        # 4 块精细化处理(长切短合)
        sections = self._step_4_refine_chunks(sections)

        # 5 打印日志
        self._step_5_print_stats(lines_count, sections)

        # 6 备份
        self._step_6_backup(state, sections)

        state["chunks"] = None
        return state
