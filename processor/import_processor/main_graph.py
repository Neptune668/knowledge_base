class KBImportWorkflow:
    def __init__(self, **kwargs):
        self._compiled_graph = None
    @property
    def graph(self):
        if self._compiled_graph is None:
            self