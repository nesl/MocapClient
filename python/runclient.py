#!/usr/bin/python
# --- IMPORTS ---
from Mocap import *

mc = MocapClient('224.0.0.1', 1510, 1511)
for frame in mc.listen():
	print 'Received frame with ID: %d' % frame.getFrameNum()
	print '-----------------------------------'
	for rb in frame.getRigidBodies():
		print rb
	print ''