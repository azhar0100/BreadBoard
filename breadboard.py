import numpy as np

class BreadBoard(object):
	"""The breadboard class should somehow only expose the nodes that are joined.
	That is somebody outside should not be able to differentiate two holes that are actually on the same node"""
	def __init__(sizeofonerow,upperrail,lowerrail):
		self.nodes = []

