import os
import signal
import logging
import traceback

from datetime import datetime
from typing import Optional, Type
from .component import Component
from multiprocessing import Process, Queue
from .exceptions import InerruptSignalExc, StopRequestExc
from .utils.fps_counter import FPSCounter


class Worker:
    """Worker class for the pipeline. It runs a component in a separate process and maintains a loop for reading and processing data."""

    def __init__(self, name: str, component_class: Type[Component], log_interval: int = 20):
        """Initializes the worker."""
        self.name = name
        self.component_class = component_class
        self.process = Process(target=self._run_loop)
        self.input_queue: Optional[Queue] = Queue()
        self.output_queue: Optional[Queue] = None
        self.fps_counter = FPSCounter()
        self.log_interval = log_interval

    def start(self):
        """Starts the worker."""
        self.process.start()
    
    def join(self):
        """Joins the worker."""
        self.process.join()

    def terminate(self):
        """Terminates the worker."""
        if self.process.is_alive():
            self.process.terminate()
    
    def _run_loop(self):
        """Runs the loop for reading and processing data."""
        logger = logging.getLogger(self.name)
        logger.info('worker started')
        is_stopped = False
        component: Optional[Component] = None
        try:
            def signal_handler(sig, frame):
                logger.debug(f'signal {signal.Signals(sig).name} received, stopping...')
                nonlocal is_stopped
                if not is_stopped:
                    is_stopped = True
                    raise InerruptSignalExc
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            component = self.component_class(name=self.name)

            while True:
                self.fps_counter.tick()
                input_data = component.read(self.input_queue)
                frame_id = input_data['frame_id']
                timestamp = input_data['timestamp']
                output_data = component.process(input_data)
                if output_data is not None and self.output_queue is not None:
                    self.output_queue.put(output_data)
                if frame_id % self.log_interval == 0:
                    latency = (datetime.now() - timestamp).total_seconds()
                    log_str_components = [
                        f'frame_id={frame_id}',
                        f'fps={self.fps_counter.fps:.1f}',
                        f'latency={latency:.3f}s',
                        f'qsize={self.input_queue.qsize()}'
                    ]
                    log_str = ''
                    for c in log_str_components:
                        log_str += f'{c:<18s}'
                    logger.info(log_str)
        except InerruptSignalExc:
            # we don't need to do anything here because parent process will handle the signal
            pass
        except StopRequestExc:
            # we need to notify parent process that we are going to stop
            is_stopped = True
            os.kill(os.getppid(), signal.SIGTERM.value)
        except Exception as e:
            is_stopped = True
            # all other exceptions are considered as internal errors of the current component
            # therefore, we need to terminate the parent process
            logger.error(traceback.format_exc())
            os.kill(os.getppid(), signal.SIGTERM.value)
        finally:
            is_stopped = True
            if component is not None:
                del component
            logger.info('worker ended')
