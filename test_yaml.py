from yaml import safe_load

xx = None
path = '/coyote/coyote_tasks.yaml'
with open(path) as f:
    xx = safe_load(f)

import ipdb;ipdb.set_trace()
