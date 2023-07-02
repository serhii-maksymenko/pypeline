import time
import logging

from typing import Any
from multiprocessing import Queue


class Component:
    """Base class for components."""

    def __init__(self, name: str):
        """
        Initializes the component.
        Args:
            name (str): Name of the component.    
        """
        self.name = name
        self.logger = logging.getLogger(self.name)

    def read(self, input_queue: Queue) -> Any:
        """
        Reads data from the input queue or from any other source in subclasses. 
        Although, reading from the default input queue is the most common case, it is still optional.
        frame_id and timestamp are required in the input data.
        Args:
            input_queue (Queue): Input queue.
        Returns:
            Any: Data read from the input queue or from any other source in subclasses.
        """
        return input_queue.get()

    def process(self, input_data: Any) -> Any:
        """
        Processes the data. This method can be implemented in subclasses. If not implemented, it will ba a pass-through.
        Args:
            input_data (Any): Input data.
        Returns:
            Any: Output data.
        """
        return input_data

    def close(self):
        """
        Closes the component. This method can be implemented in subclasses for clean-up.
        """
        pass

    def __del__(self):
        self.close()
        self.logger.debug('closed')
