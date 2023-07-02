import time
import signal
import logging
import traceback

from typing import List
from .worker import Worker


class Pipeline:

    def __init__(self):
        """
        Initializes the pipeline.
        """
        self.workers: List[Worker] = []
        self.logger = logging.getLogger('pipeline')
    
    def add_worker(self, worker: Worker):
        """
        Adds a worker to the pipeline.
        Args:
            worker (Worker): Worker to be added.
        """
        if len(self.workers) > 0:
            self.workers[-1].output_queue = worker.input_queue
        self.workers.append(worker)

    def _terminate_workers(self):
        for worker in self.workers:
            worker.terminate()
    
    def _start_workers(self):
        for worker in self.workers:
            worker.start()
            while not worker.process.is_alive():
                time.sleep(0.005)

    def start(self):
        """Starts all workers in the pipeline."""
        try:
            def signal_handler(sig, frame):
                self.logger.debug(f'signal {signal.Signals(sig).name} received, terminating workers...')
                self._terminate_workers()
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            self._start_workers()
            self.logger.info('pipeline started')
            for worker in self.workers:
                worker.join()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self._terminate_workers()
        finally:
            self.logger.info('pipeline ended')
    