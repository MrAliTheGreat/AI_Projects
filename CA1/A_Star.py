import time
from heapq import heapify, heappush, heappop

class MinHeap():
	def __init__(self):
		self.heap = []
		heapify(self.heap)
		self.index = 0
		

	def push(self , element , priority):
		heappush(self.heap , (priority , self.index , element))
		self.index += 1 # for elements with equal priority

	def pop(self):
		return heappop(self.heap)[-1]

	def top(self):
		return self.heap[0]

	def isEmpty(self):
		if(len(self.heap) == 0):
			return True
		return False

	def printHeap(self):
		for priority , _ , element in self.heap:
			print("Priority: " + str(priority) + " element: " + str(element))



class State():
	def __init__(self, curLoc_x , curLoc_y , curCapacity , curNumRemainingBalls , needDelivery , hasPicked ,
				 parentState=None , depth=0):

		self.curLoc_x = curLoc_x
		self.curLoc_y = curLoc_y
		self.curCapacity = curCapacity
		self.curNumRemainingBalls = curNumRemainingBalls
		self.needDelivery = needDelivery
		self.parentState = parentState
		self.hasPicked = hasPicked
		
		if(self.parentState is None):
			self.depth = 0
		else:
			self.depth = self.parentState.depth + 1

	# def __eq__(self , other):
	# 	return self.curLoc_x == other.curLoc_x and self.curLoc_y == other.curLoc_y and \
	# 		   self.curNumRemainingBalls == other.curNumRemainingBalls

	def getHash(self):
		strNeedDelivery = "".join([str(t) for t in self.needDelivery])
		if(self.parentState is None):
			strParent = "-00"
		else:
			strParent = str(self.parentState.curLoc_x) + str(self.parentState.curLoc_y)
		
		return str(self.curLoc_x) + str(self.curLoc_y) + str(self.curNumRemainingBalls) + strNeedDelivery + strParent

	def getNumPicked(self):
		return len(self.hasPicked)

	def getCurLoc_x(self):
		return self.curLoc_x

	def getCurLoc_y(self):
		return self.curLoc_y

	def getCurCapacity(self):
		return self.curCapacity

	def getCurNumRemainingBalls(self):
		return self.curNumRemainingBalls

	def getNeedDelivery(self):
		return self.needDelivery

	def getHasPicked(self):
		return self.hasPicked

	def getParentState(self):
		return self.parentState

	def getDepth(self):
		return self.depth

	def setCurCapacity(self , newValue):
		self.curCapacity = newValue

	def setCurNumRemainingBalls(self , newValue):
		self.curNumRemainingBalls = newValue

	def setNeedDelivery(self , newValue):
		self.needDelivery = newValue

	def setHasPicked(self , newValue):
		self.hasPicked = newValue



def getMazeElement(maze , x , y):
	return maze[x][y * 2]


def isValidInMaze(maze , x , y , num_rows , num_columns):
	if(x >= 0 and y >= 0 and x < num_rows and y < num_columns and getMazeElement(maze , x , y) != '*'):
		return True

	return False


def updateFrontier(frontier , newState , goal_x , goal_y , explored , num_balls , ballsInitLocs , ballsDestLocs):
	frontier.push(newState , calculateF(newState , goal_x , goal_y , num_balls , ballsInitLocs , ballsDestLocs))
	explored.add(newState.getHash())
	
	if(newState.getCurLoc_x() == goal_x and newState.getCurLoc_y() == goal_y and newState.getCurNumRemainingBalls() == 0):
		return True
	
	return False


def placeBall(maze , curState , ballsDestLocs):
	if(len(curState.getNeedDelivery()) <= 0):
		return

	try:
		deliveryIndex = curState.getNeedDelivery().index((curState.getCurLoc_x() , curState.getCurLoc_y()))
	except ValueError:
		return

	curStateNeedDelivery = list(curState.getNeedDelivery())
	del curStateNeedDelivery[deliveryIndex]
	curState.setNeedDelivery(curStateNeedDelivery)

	curState.setCurCapacity(curState.getCurCapacity() + 1)
	curState.setCurNumRemainingBalls(curState.getCurNumRemainingBalls() - 1)


def grabBall(maze , curState , ballsInitLocs , ballsDestLocs , frontier , goal_x , goal_y , num_balls , explored ,
			 numExploredStates):

	if(curState.getCurCapacity() <= 0):
		return numExploredStates

	try:
		ballIndex = ballsInitLocs.index((curState.getCurLoc_x() , curState.getCurLoc_y()))
	except ValueError:
		return numExploredStates

	if((curState.getCurLoc_x() , curState.getCurLoc_y()) in curState.getHasPicked()):
		return numExploredStates

	newNeedDelivery = list(curState.getNeedDelivery())
	newNeedDelivery.append(ballsDestLocs[ballIndex])

	newHasPicked = list(curState.getHasPicked())
	newHasPicked.append((curState.getCurLoc_x() , curState.getCurLoc_y()))

	newState = State(curState.getCurLoc_x() , curState.getCurLoc_y() , curState.getCurCapacity() - 1 , 
					 curState.getCurNumRemainingBalls() , newNeedDelivery , newHasPicked , curState)

	if(newState.getHash() not in explored):
		frontier.push(newState , calculateF(newState , goal_x , goal_y , num_balls , ballsInitLocs , ballsDestLocs))
		explored.add(newState.getHash())
		return numExploredStates + 1

	return numExploredStates


def findManhattanDistance(x1 , y1 , x2 , y2):
	return abs(x2 - x1) + abs(y2 - y1)


def findMinHeuPicking(curState , ballsInitLocs , ballsDestLocs , num_balls , hasPicked):
	minCost = float("inf")
	
	for i in range(num_balls):
		# plus 1 for picking the ball up
		if(ballsInitLocs[i] not in hasPicked):
			cost = findManhattanDistance(curState.getCurLoc_x() , curState.getCurLoc_y() , ballsInitLocs[i][0] , ballsInitLocs[i][1]) + \
				   findManhattanDistance(ballsInitLocs[i][0] , ballsInitLocs[i][1] , ballsDestLocs[i][0] , ballsDestLocs[i][1]) + 1

			if(cost < minCost):
				minCost = cost

	return minCost


def findMinHeuDelivery(curState):
	minCost = float("inf")

	for put_x , put_y in curState.getNeedDelivery():
		# plus 1 for picking the ball up
		cost = findManhattanDistance(curState.getCurLoc_x() , curState.getCurLoc_y() , put_x , put_y)

		if(cost < minCost):
			minCost = cost

	return minCost


def calculateF(curState , goal_x , goal_y , num_balls , ballsInitLocs , ballsDestLocs):
	# Picking up a ball is a move so it's used in f calculation

	# Heuristic 1 --> Surely Admissible , Consistence
	if(curState.getCurNumRemainingBalls() == 0):
		return curState.getDepth() + curState.getNumPicked() + \
			   findManhattanDistance(curState.getCurLoc_x() , curState.getCurLoc_y() , goal_x , goal_y)

	if(len(curState.getNeedDelivery()) == 0):
		return curState.getDepth() + curState.getNumPicked() + \
			   findMinHeuPicking(curState , ballsInitLocs , ballsDestLocs , num_balls , curState.getHasPicked())

	if(curState.getCurCapacity() == 0):
		return curState.getDepth() + curState.getNumPicked() + \
			   findMinHeuDelivery(curState)

	return curState.getDepth() + curState.getNumPicked() + \
		   min(findMinHeuDelivery(curState) ,
		   	   findMinHeuPicking(curState , ballsInitLocs , ballsDestLocs , num_balls , curState.getHasPicked()))
	
	# # Heuristic 2 --> Surely Consistent , Addmissible
	# if(curState.getCurNumRemainingBalls() == 0):
	# 	return curState.getDepth() + curState.getNumPicked() + \
	# 			findManhattanDistance(curState.getCurLoc_x() , curState.getCurLoc_y() , goal_x , goal_y)
	
	# return curState.getDepth() + curState.getNumPicked() + curState.getCurNumRemainingBalls()



def A_Star(maze , num_rows , num_columns , start_x , start_y , goal_x , goal_y , capacity , num_balls , ballsInitLocs ,
		   ballsDestLocs):

	frontier = MinHeap()
	explored = set()

	start_state = State(start_x , start_y , capacity , num_balls , [] , [])
	frontier.push(start_state , calculateF(start_state , goal_x , goal_y , num_balls , ballsInitLocs , ballsDestLocs))
	explored.add(start_state.getHash())

	uniqueExplored = set()
	numExploredStates = 0; numUniqueExploredStates = 0

	if(start_x == goal_x and start_y == goal_y and num_balls == 0):
		return frontier.top() , numExploredStates , numUniqueExploredStates

	while(not frontier.isEmpty()):
		curState = frontier.pop()

		if(curState.getHash() not in uniqueExplored):
			numUniqueExploredStates += 1
			uniqueExplored.add(curState.getHash())
		
		numExploredStates = grabBall(maze , curState , ballsInitLocs , ballsDestLocs , frontier , goal_x , goal_y ,
									 num_balls , explored , numExploredStates)
		placeBall(maze , curState , ballsDestLocs)

		if(isValidInMaze(maze , curState.getCurLoc_x() , curState.getCurLoc_y() - 1 , num_rows , num_columns)): # Left
			newState = State(curState.getCurLoc_x() , curState.getCurLoc_y() - 1 , curState.getCurCapacity() ,
							 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
							 curState)

			if(newState.getHash() not in explored):
				numExploredStates += 1
				if(updateFrontier(frontier , newState , goal_x , goal_y , explored , num_balls , ballsInitLocs , ballsDestLocs)):
					return newState , numExploredStates , numUniqueExploredStates

		if(isValidInMaze(maze , curState.getCurLoc_x() + 1 , curState.getCurLoc_y() , num_rows , num_columns)): # Down
			newState = State(curState.getCurLoc_x() + 1 , curState.getCurLoc_y() , curState.getCurCapacity() ,
							 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
							 curState)

			if(newState.getHash() not in explored):
				numExploredStates += 1
				if(updateFrontier(frontier , newState , goal_x , goal_y , explored , num_balls , ballsInitLocs , ballsDestLocs)):
					return newState , numExploredStates , numUniqueExploredStates				

		if(isValidInMaze(maze , curState.getCurLoc_x() - 1 , curState.getCurLoc_y() , num_rows , num_columns)): # Up
			newState = State(curState.getCurLoc_x() - 1 , curState.getCurLoc_y() , curState.getCurCapacity() ,
							 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
							 curState)						
			
			if(newState.getHash() not in explored):
				numExploredStates += 1
				if(updateFrontier(frontier , newState , goal_x , goal_y , explored , num_balls , ballsInitLocs , ballsDestLocs)):
					return newState , numExploredStates , numUniqueExploredStates

		if(isValidInMaze(maze , curState.getCurLoc_x() , curState.getCurLoc_y() + 1 , num_rows , num_columns)): # Right
			newState = State(curState.getCurLoc_x() , curState.getCurLoc_y() + 1 , curState.getCurCapacity() ,
							 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
							 curState)
			
			if(newState.getHash() not in explored):
				numExploredStates += 1
				if(updateFrontier(frontier , newState , goal_x , goal_y , explored , num_balls , ballsInitLocs , ballsDestLocs)):
					return newState , numExploredStates , numUniqueExploredStates




def getNumAndPrintActions(firstState , printActions = False):
	num_levels = 0
	if(firstState is None):
		return num_levels

	while(firstState.getParentState() is not None):
		if(printActions):
			print(str(firstState.getCurLoc_x()) + " " + str(firstState.getCurLoc_y()) + 
					" capacity: " + str(firstState.getCurCapacity()) )
		firstState = firstState.getParentState()
		num_levels += 1

	return num_levels


for i in range(1 , 5):
	testFile = open("Tests/" + str(i) + ".txt" , "r")
	inputs = testFile.read().splitlines()
	testFile.close()

	num_rows , num_columns = list(map(int , inputs[0].split()))
	start_x , start_y = list(map(int , inputs[1].split()))
	goal_x , goal_y = list(map(int , inputs[2].split()))
	capacity = int(inputs[3])
	num_balls = int(inputs[4])
	ballsInitLocs = []
	ballsDestLocs = []
	for i in range(num_balls):
		s_x , s_y , d_x , d_y = list(map(int , inputs[5 + i].split()))
		ballsInitLocs.append((s_x , s_y)); ballsDestLocs.append((d_x , d_y))

	maze = inputs[5 + num_balls :]


	tic = time.time()
	goalState , numExploredStates , numUniqueExploredStates = A_Star(maze , num_rows , num_columns , start_x , start_y ,
																	 goal_x , goal_y , capacity , num_balls ,
																	 ballsInitLocs , ballsDestLocs)
	toc = time.time()


	num_levels = getNumAndPrintActions(goalState)

	print("Num of levels: " + str(num_levels))
	print("Number of explored States: " + str(numExploredStates))
	print("Number of unique explored States: " + str(numUniqueExploredStates))
	print("Time: " + str(toc - tic) + " s")
	print("=================")
