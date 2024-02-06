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

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


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
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		points.sort(key=lambda point: point.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]

		node = divideConquer(points)
		currNode = node
		nodes = []
		while True:
			nextNode = currNode.next
			nodes.append(QLineF(currNode.data, nextNode.data))
			currNode = nextNode
			if currNode == node:
				break

		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(nodes,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

def divideConquer(points):
	if (len(points) == 2):
		node1 = Node(points[0])
		node2 = Node(points[1])
		node1.next = node2
		node1.prev = node2
		node2.next = node1
		node2.prev = node1
		return node1
	if (len(points) == 3):
		node1 = Node(points[0])
		node2 = Node(points[1])
		node3 = Node(points[2])
		slope2 = slopeFinder(node1, node2)
		slope3 = slopeFinder(node1, node3)
		if (slope2 > slope3):
			node1.next = node2
			node2.next = node3
			node3.next = node1
			node1.prev = node3
			node3.prev = node2
			node2.prev = node1
		else:
			node1.next = node3
			node3.next = node2
			node2.next = node1
			node1.prev = node2
			node2.prev = node3
			node3.prev = node1
		return node1
	L,R = splitLR(points)
	left = divideConquer(L)
	right = divideConquer(R)
	return findTangents(left,right)

def splitLR(points):
	mid = len(points) // 2
	L = points[:mid]
	R = points[mid:]
	return L,R

def slopeFinder(n1, n2):
	return ((n2.data.y() - n1.data.y())/(n2.data.x() - n1.data.x()))

def findMax(L):
	head = L
	maxX = L.data.x()
	maxNode = L
	current_node = L.next

	while current_node is not head:
		if current_node.data.x() > maxX:
			maxX = current_node.data.x()
			maxNode = current_node
		current_node = current_node.next

	return maxNode

def findMin(R):
	head = R
	minX = R.data.x()
	minNode = R
	current_node = R.next

	while current_node is not head:
		if current_node.data.x() < minX:
			minX = current_node.data.x()
			minNode = current_node
		current_node = current_node.next

	return minNode

def findTangents(L,R):

	leftMax = findMax(L)
	rightMin = findMin(R)
	l = leftMax
	r = rightMin
	lc = leftMax
	rc = rightMin

	isLeft = True
	leftDone = False
	rightDone = False
	while not (leftDone and rightDone):
		if (isLeft):
			preslopeL = slopeFinder(l,r)
			postslopeL = slopeFinder(l.prev,r)
			if (preslopeL > postslopeL):
				l = l.prev
				rightDone = False
			else:
				leftDone = True
		else:
			preslopeR = slopeFinder(l,r)
			postslopeR = slopeFinder(l,r.next)
			if (preslopeR < postslopeR):
				r = r.next
				leftDone = False
			else:
				rightDone = True
		isLeft = not isLeft

	isLeft = True
	leftDone = False
	rightDone = False
	while not (leftDone and rightDone):
		if (isLeft):
			preslopeL = slopeFinder(lc,rc)
			postslopeL = slopeFinder(lc.next,rc)
			if (preslopeL < postslopeL):
				lc = lc.next
				rightDone = False
			else:
				leftDone = True
		else:
			preslopeR = slopeFinder(lc,rc)
			postslopeR = slopeFinder(lc,rc.prev)
			if (preslopeR > postslopeR):
				rc = rc.prev
				leftDone = False
			else:
				rightDone = True
		isLeft = not isLeft

	l.next = r
	r.prev = l
	rc.next = lc
	lc.prev = rc

	return rc