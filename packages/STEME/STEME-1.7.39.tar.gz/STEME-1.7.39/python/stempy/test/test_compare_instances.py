#
# Copyright John Reid 2012
#

"""
Test compare instances. There seems to be a problem with stempy.InstanceVec.
"""

from setup_environment import init_test_env, update_path_for_stempy, logging
init_test_env(__file__, level=logging.INFO)
update_path_for_stempy()

import stempy

W = 10
instances = stempy.InstanceVec()
for i in xrange(0, 100, W):
    instances.append(stempy.FindBestWMers.Evaluation(.9, i, True))
overlap, start_size, discretized_size = stempy.compare_instances(instances, W, instances, W)
