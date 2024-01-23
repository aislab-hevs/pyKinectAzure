import numpy as np
import cv2

from pykinect_azure.k4abt.joint2d import Joint2d
from pykinect_azure.k4abt._k4abtTypes import K4ABT_JOINT_COUNT, K4ABT_SEGMENT_PAIRS
from pykinect_azure.k4abt._k4abtTypes import k4abt_skeleton2D_t, k4abt_body2D_t, body_colors
from pykinect_azure.k4a._k4atypes import K4A_CALIBRATION_TYPE_DEPTH

class Body2d:
	def __init__(self, body2d_handle):
		self.joints = None

		if body2d_handle:
			self._handle = body2d_handle
			self.id = body2d_handle.id
			self.initialize_skeleton()

	def __del__(self):
		self.destroy()

	def json(self):
		return self._handle.__iter__()

	def numpy(self):
		return np.array([joint.numpy() for joint in self.joints])

	def is_valid(self):
		return self._handle

	def handle(self):
		return self._handle

	def destroy(self):
		if self.is_valid():
			self._handle = None

	def initialize_skeleton(self):
		joints = np.ndarray((K4ABT_JOINT_COUNT,),dtype=np.object_)

		for i in range(K4ABT_JOINT_COUNT):
			joints[i] = Joint2d(self._handle.skeleton.joints2D[i], i)

		self.joints = joints

	def draw(self, image, only_segments = False, show_id = False):
		for segment_id in range(len(K4ABT_SEGMENT_PAIRS)):
			segment_pair = K4ABT_SEGMENT_PAIRS[segment_id]
			point1 = self.joints[segment_pair[0]].get_coordinates()
			point2 = self.joints[segment_pair[1]].get_coordinates()

			if (point1[0] == 0 and point1[1] == 0) or (point2[0] == 0 and point2[1] == 0):
				continue

			image = cv2.line(image, point1, point2, self.color, 2)

		if show_id:
			image = cv2.putText(img=image,
								text=str(self.id),
								org=(self.joints[27].position.x, self.joints[27].position.y),
								fontFace=cv2.FONT_HERSHEY_SIMPLEX,
								fontScale=1,
								color=(255, 255, 255), # white
								thickness=1,
								lineType=cv2.LINE_AA)

		if only_segments:
			return image

		for joint in self.joints:
			image = cv2.circle(image, joint.get_coordinates(), 3, self.color, 3)

		return image

	@property
	def color(self, unique_colors=200):
		total_colors = 256 ** 3
		hex_color = self.id * int(total_colors / unique_colors)
		r = (hex_color >> 16) & 0xFF
		g = (hex_color >> 8) & 0xFF
		b = hex_color & 0xFF
		return [r, g, b]


	@staticmethod
	def create(body_handle, calibration, bodyIdx, dest_camera):

		skeleton2d_handle = k4abt_skeleton2D_t()
		body2d_handle = k4abt_body2D_t()

		for jointID,joint in enumerate(body_handle.skeleton.joints): 
			skeleton2d_handle.joints2D[jointID].position = calibration.convert_3d_to_2d(joint.position, K4A_CALIBRATION_TYPE_DEPTH, dest_camera)
			skeleton2d_handle.joints2D[jointID].confidence_level = joint.confidence_level

		body2d_handle.skeleton = skeleton2d_handle
		body2d_handle.id = bodyIdx

		return Body2d(body2d_handle)


	def __str__(self):
		"""Print the current settings and a short explanation"""
		message = f"Body Id: {self.id}\n\n"

		for joint in self.joints:
			message += str(joint)

		return message

