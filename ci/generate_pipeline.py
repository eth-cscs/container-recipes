import os
import yaml
#import pathlib
#
#prefix = pathlib.Path(__file__).parent.resolve()
#root_path = prefix.parent.resolve()

DIR = os.getenv('dir')

pipeline = {
    "include" : [{"local" : f"{DIR}/ci.yaml"}]
}

with open("pipeline.yml", "w") as f:
    yaml.dump(pipeline, f)




