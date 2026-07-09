import json
import logging
from pathlib import Path

from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError, FileProcessingError
from processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    name = "node_pdf_to_md"

    def process(self, state: ImportGraphState):
        logging.info(f"{self.name}节点开始执行...")
        # 1 检查和获取相关参数
        # 2 获取上传链接并上传文件到mineru服务器
        # 3 下载zip压缩文件并且解压改名
        # 4 读取文件md_content


        # 1 校验路径
        # 2 path封装路径
        # 3 文档是否存在
