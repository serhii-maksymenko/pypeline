import cv2
import logging
from pypeline import Pipeline, Worker, Component, FrameMetadataGenerator
from pypeline.exceptions import StopRequestExc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)20s - %(levelname)7s - %(message)s')


class VideoSource(Component):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap = cv2.VideoCapture(0)
        self.frame_metadata_generator = FrameMetadataGenerator()
    
    def read(self, input_queue):
        frame_metadata = self.frame_metadata_generator.generate()
        flag, frame = self.cap.read()
        if not flag:
            raise StopRequestExc
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        frame_metadata['frame'] = frame
        return frame_metadata
    
    def close(self):
        self.cap.release()


class GrayscaleFilter(Component):
    
    def process(self, input_data):
        frame = input_data.pop('frame')
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        input_data['filtered_frame'] = frame

        return input_data
    

class Presenter(Component):
    
    def process(self, input_data):
        filtered_frame = input_data['filtered_frame']
        filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_GRAY2BGR)
        cv2.imshow('presented frame', filtered_frame)
        key = cv2.waitKey(20)
        if key == ord('q'):
            raise StopRequestExc
        return None


pipeline = Pipeline()
pipeline.add_worker(Worker('video_source', VideoSource))
pipeline.add_worker(Worker('grayscale_filter', GrayscaleFilter))
pipeline.add_worker(Worker('presenter', Presenter))
pipeline.start()
