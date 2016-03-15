#!/usr/bin/python
# --- IMPORTS ---
import time
from Mocap import *

mc = MocapClient('224.0.0.1', 1510, 1511)
tstart = time.time()

for frame in mc.listen():
	# print 'Received frame with ID: %d' % frame.getFrameNum()
	# print '-----------------------------------'
	t = time.time() - tstart
	for rb in frame.getRigidBodies():
		print t*1e3, rb.getPosition()[0], rb.getPosition()[1], rb.getPosition()[2], rb.getQuaternion()[0], rb.getQuaternion()[1], rb.getQuaternion()[2]
	# print ''