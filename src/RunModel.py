from Pipeline import Pipeline
from Memory import Memory
from Definitions import *

# This class creates and run the Pipeline model
# Receive two parameters dictionary memory and pipeline
#  - mem_params - response on loading the memory
#  - pipeline_params - behavior of the pipeline
class RunModel:

    def __init__(self, mem_params: dict, pipeline_params=dict()):
        self.pipeline_params = pipeline_params
        self.memory = Memory(mem_params)
        self.pipeline = Pipeline(self.memory, pipeline_params)

    def simulator(self):
        params = self.pipeline_params
        prefetch_ae =  params["PREFETCH_AE"] == "True" if "PREFETCH_AE" in params.keys() else PREFETCH_AE
        bp_en =  params["BP_EN"] == "True" if "BP_EN" in params.keys() else BP_EN
        issue_policy = params["ISSUE_POLICY"] if "ISSUE_POLICY" in params.keys() else ISSUE_POLICY

        if(issue_policy == "EVENT_AE") and not ( (bp_en == True) or (prefetch_ae == True) ):
            return

        cur_tick = 0
        while self.pipeline.tick(cur_tick):
            cur_tick += 1

    def report_statistics(self):
        self.pipeline.report_model()
        self.pipeline.report_statistics()
