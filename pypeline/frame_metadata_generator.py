from datetime import datetime


class FrameMetadataGenerator:

    def __init__(self):
        self.frame_id = -1
    
    def generate(self):
        """Returns frame metadata with frame_id and timestamp. Timestamp is the current time which is needed to calculate latency in the component."""
        self.frame_id += 1
        return {
            'frame_id': self.frame_id,
            'timestamp': datetime.now()
        }