import logging
from pathlib import Path

from processor.import_processor.base import BaseNode
from processor.import_processor.exceptions import StateFieldError, FileProcessingError
from processor.import_processor.state import ImportGraphState


def process(self, state: ImportGraphState):
    logging.info(f"{self.name}节点开始执行...")

    return state