import time


class FPSCounter:

    def __init__(self):
        self.ticks = []
        self.fps = 0
    
    def tick(self):
        tick = time.perf_counter()
        num_ticks = len(self.ticks)
        if num_ticks > 0 and (tick - self.ticks[0]) > 1:
            self.fps = num_ticks
            self.ticks.clear()
        self.ticks.append(tick)
