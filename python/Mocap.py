# --- IMPORTS ---
import socket
import struct
import time

class MocapFrame:
	def __init__(self):
		self._rigidBodies = []
		self._skeletons = []
		self._markers = []
		self._framenum = 0
		self._timestamp = 0

	def setFrameNum(self, num):
		self._framenum = num

	def getFrameNum(self):
		return self._framenum

	def addRigidBody(self, rb):
		self._rigidBodies.append(rb)

	def getRigidBodies(self):
		return self._rigidBodies


class RigidBody:
	def __init__(self, uid, xyz, quat):
		self._id = uid
		self._xyz = xyz
		self._quat = quat

	def getId(self):
		return self._id

	def getPosition(self):
		return self._xyz

	def getQuaternion(self):
		return self._quat		

	def __str__(self):
		return "Rigid Body [%d] @ (%.3f, %.3f, %.3f)" % (self._id, self._xyz[0], self._xyz[1], self._xyz[2])


class MocapClient:

	def __init__(self, mcast_group, cmd_port, clnt_port):
		self._connected = False
		self._cmd_port = cmd_port
		self._clnt_port = clnt_port
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self._sock.bind(('', clnt_port))
			self._connected = True
			mreq = struct.pack("4sl", socket.inet_aton(mcast_group), socket.INADDR_ANY)
			self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		except:
			raise  OSError('Cannot bind to specified address and port')

	def disconnect(self):
		self._connected = False

	# listen for inbound traffic
	def listen(self):
		# connect if not connected yet
		if not self._connected:
			return;

		while self._connected:
			time.sleep(0.01)
			data = self._sock.recv(2048)
			frame = self._parseRawData(data)
			yield frame

	def _parseRawData(self, bytes):
		# mocap frame to be returned
		frame = MocapFrame()
		# index begins at byte 0 and is advanced along the way
		idx = 0
		# skip 4 bytes header and size
		idx += 4
		# read frame number
		num = struct.unpack("I", bytes[idx:(idx+4)])[0]
		frame.setFrameNum( num )
		idx += 4

		# MARKER SETS
		numMarkerSets = struct.unpack("I", bytes[idx:(idx+4)])[0]
		idx += 4
		for i in range(numMarkerSets):
			# ignore name by reading until null terminator found
			while bytes[idx] != '\0':
				idx += 1
			# skip over null terminator
			idx += 1
			# number of markers in set
			numMarkersInSet = struct.unpack("I", bytes[idx:(idx+4)])[0]
			idx += 4
			for j in range(numMarkersInSet):
				# ignore marker position
				idx += 3*4

		# OTHER MARKERS
		numMarkers = struct.unpack("I", bytes[idx:(idx+4)])[0]
		idx += 4
		for i in range(numMarkers):
			# ignore unmarked markers for now
			idx += 3*4

		# RIGID BODIES
		numRigidBodies = struct.unpack("I", bytes[idx:(idx+4)])[0]
		idx += 4

		for i in range(numRigidBodies):
			# ID
			uid = struct.unpack("I", bytes[idx:(idx+4)])[0]
			idx += 4
			# position
			px = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			py = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			pz = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			xyz = (px,py,pz)
			# pose
			qx = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			qy = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			qz = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			qw = struct.unpack("f", bytes[idx:(idx+4)])[0]
			idx += 4
			orientation = (qx, qy, qz, qw)

			# create rigid body
			rb = RigidBody(uid, xyz, orientation)

			# number of markers
			numMarkers = struct.unpack("I", bytes[idx:(idx+4)])[0]
			idx += 4

			if numMarkers > 0:
				# skip markers
				idx += numMarkers*(4*3)
				# skip marker IDs
				idx += numMarkers*4
				# skip marker sizes
				idx += numMarkers*4

				# skip mean marker error
				idx += 4

				# read rigid body params
				params = struct.unpack("H", bytes[idx:(idx+2)])[0]
				idx += 2

			# if RB is tracked
			if params & 1:
				frame.addRigidBody( rb )

		# SKELETONS
		numSkeletons = struct.unpack("I", bytes[idx:(idx+4)])[0]
		idx += 4
		# TODO

		# skip labeled markers
		idx += 4

		# skip force plates
		idx += 4

		# skip latency (float)
		idx += 4

		# skip timecode
		idx += 4

		# skip timecode sub
		idx += 4

		# skip timestamp
		idx += 8

		# skip params
		idx += 2

		return frame