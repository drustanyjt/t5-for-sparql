class BaseMasker:

    def __init___(self, name="BaseLinker"):
        self.name = name
    
    def mask(self, str):
        raise NotImplementedError

    def unmask(self, str):
        raise NotImplementedError

class BaseProcessor:
    """Base class for handling data preprocessing and standardising output"""

    def __init__(self, dataset_path: str, name="BaseProcessor"):
        """Creates a BaseProcessor with the given dataset

        Args:
            dataset_path (str): Path to dataset.
            name (str, optional): Name of processor. Defaults to "BaseProcessor".
        """
        self.dataset_path = dataset_path
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def preprocessor(self):
        raise NotImplementedError
    
    
    
class BaseLinker:
    """Base class for entity or relation linking"""

    def __init__(self, name="BaseLinker"):
        self.name = name
    
    def link(self, query: str):
        raise NotImplementedError

class BaseModel:
    """Base class for LLMs"""

    def __init__(self, name="BaseModel"):
        self.name = name
    
    def train(self):
        raise NotImplementedError