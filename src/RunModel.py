from Pipeline import Pipeline
from Memory import Memory


# This class creates and run the Pipeline model
# Receive two parameters dictionary memory and pipeline
#  - mem_params - response on loading the memory
#  - pipeline_params - behavior of the pipeline
class RunModel:

    def __init__(self, mem_params: dict, pipeline_params=dict()):
        self.memory = Memory(mem_params)
        self.pipeline = Pipeline(self.memory, pipeline_params)

    def simulator(self):
        cur_tick = 0
        while self.pipeline.tick(cur_tick):
            cur_tick += 1

    def report_statistics(self):
        self.pipeline.report_model()
        self.pipeline.report_statistics()
