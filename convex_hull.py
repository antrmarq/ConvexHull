from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		sortedPoints = sorted(points, key=lambda k: k.x())
		t2 = time.time()

		t3 = time.time()

		node = divide_and_conquer(sortedPoints)
		polygon = to_qlinef_list(node)
		t4 = time.time()

		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

def divide_and_conquer(points):
	# Divide and conquer algorithm to find the convex hull of a set of points
    num_points = len(points)
    if num_points <= 1:
        hull_root_node = double_linked_list(points)
        return hull_root_node

    left_hull_root = divide_and_conquer(points[:num_points // 2])
    right_hull_root = divide_and_conquer(points[num_points // 2:])

    upper_left_tangent_node, upper_right_tangent_node, lower_left_tangent_node, lower_right_tangent_node = find_tangents(left_hull_root, right_hull_root)

    # Connect upper tangent
    upper_left_tangent_node.next = upper_right_tangent_node
    upper_right_tangent_node.prev = upper_left_tangent_node

    # Connect lower tangent
    lower_right_tangent_node.next = lower_left_tangent_node
    lower_left_tangent_node.prev = lower_right_tangent_node

    return upper_left_tangent_node

def find_tangents(left, right):
	# Find the upper and lower tangents of two convex hulls
	left_hull_right_most = find_right_node(left)
	right_hull_left_most = find_left_node(right)

	left_tangent_upper_point = left_hull_right_most
	right_tangent_upper_point = right_hull_left_most
	done = True
	while done:
		done = False
		previous_slope = slope(left_tangent_upper_point.point, right_tangent_upper_point.point)

		while slope(left_tangent_upper_point.prev.point, right_tangent_upper_point.point) < previous_slope:
			left_tangent_upper_point = left_tangent_upper_point.prev
			previous_slope = slope(left_tangent_upper_point.point, right_tangent_upper_point.point)
			done = True

		while slope(left_tangent_upper_point.point, right_tangent_upper_point.next.point) > previous_slope:
			right_tangent_upper_point = right_tangent_upper_point.next
			previous_slope = slope(left_tangent_upper_point.point, right_tangent_upper_point.point)
			done = True

	left_tangent_lower_point = left_hull_right_most
	right_tangent_lower_point = right_hull_left_most
	done = True
	while done:
		done = False
		previous_slope = slope(left_tangent_lower_point.point, right_tangent_lower_point.point)

		while slope(left_tangent_lower_point.next.point, right_tangent_lower_point.point) > previous_slope:
			left_tangent_lower_point = left_tangent_lower_point.next
			previous_slope = slope(left_tangent_lower_point.point, right_tangent_lower_point.point)
			done = True

		while slope(left_tangent_lower_point.point, right_tangent_lower_point.prev.point) < previous_slope:
			right_tangent_lower_point = right_tangent_lower_point.prev
			previous_slope = slope(left_tangent_lower_point.point, right_tangent_lower_point.point)
			done = True

	return left_tangent_upper_point, right_tangent_upper_point, left_tangent_lower_point, right_tangent_lower_point


def slope(p1, p2):
	# Calculate the slope of the line between two points
	return (p2.y() - p1.y()) / (p2.x() - p1.x())


class Node:
	# Helper class for finding the nodes of a circular doubly linked list
	def __init__(self, point):
		self.point = point
		self.prev = None
		self.next = None

def double_linked_list(points):
	# Create a circular doubly linked list from a list of points
	head = Node(points[0])
	tail = head
	for point in points[1:]:
		node = Node(point)
		node.prev = tail
		tail.next = node
		tail = node
	head.prev = tail
	tail.next = head
	return head

def to_qlinef_list(head):
	# Convert a circular doubly linked list to a list of QLineF
	qlinef_list = []
	node = head
	while True:
		qlinef_list.append(QLineF(node.point, node.next.point))
		node = node.next
		if node == head:
			break
	return qlinef_list

def find_right_node(head):
	# Find the rightmost node in a circular doubly linked list
	node = head
	rightmost_node = node
	while node.next != head:
		node = node.next
		if node.point.x() > rightmost_node.point.x():
			rightmost_node = node
	return rightmost_node

def find_left_node(head):
	# Find the leftmost node in a circular doubly linked list
	node = head
	leftmost_node = node
	while node.next != head:
		node = node.next
		if node.point.x() < leftmost_node.point.x():
			leftmost_node = node
	return leftmost_node