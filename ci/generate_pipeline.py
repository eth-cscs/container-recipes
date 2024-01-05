import os
import yaml
#import pathlib
#
#prefix = pathlib.Path(__file__).parent.resolve()
#root_path = prefix.parent.resolve()

APP = os.getenv('app')

pipeline = {
    "include" : [{"local" : "/ci/common.yml"}, {"local" : f"{APP}/ci.yml"}]
}

with open("pipeline.yml", "w") as f:
    yaml.dump(pipeline, f)




