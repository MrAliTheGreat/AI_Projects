import time

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

	def getHashBFS(self):
		strNeedDelivery = "".join([str(t) for t in self.needDelivery])		
		return str(self.curLoc_x) + str(self.curLoc_y) + str(self.curNumRemainingBalls) + strNeedDelivery	

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


def grabBall(maze , curState , ballsInitLocs , ballsDestLocs):
	
	if(curState.getCurCapacity() <= 0):
		return None

	try:
		ballIndex = ballsInitLocs.index((curState.getCurLoc_x() , curState.getCurLoc_y()))
	except ValueError:
		return None

	if((curState.getCurLoc_x() , curState.getCurLoc_y()) in curState.getHasPicked()):
		return None

	newNeedDelivery = list(curState.getNeedDelivery())
	newNeedDelivery.append(ballsDestLocs[ballIndex])

	newHasPicked = list(curState.getHasPicked())
	newHasPicked.append((curState.getCurLoc_x() , curState.getCurLoc_y()))

	return State(curState.getCurLoc_x() , curState.getCurLoc_y() , curState.getCurCapacity() - 1 , 
				 curState.getCurNumRemainingBalls() , newNeedDelivery , newHasPicked , curState)


def DFS(curState , maxDepth , currentPathLength , allExplored , allExploredBestLengths , dfsExplored , dfsExploredLengths ,
		maze , num_rows , num_columns , numExploredStates , numUniqueExploredStates):

	numExploredStates += 1

	if(curState.getCurLoc_x() == goal_x and curState.getCurLoc_y() == goal_y and curState.getCurNumRemainingBalls() == 0):
		return True , curState , numExploredStates , numUniqueExploredStates

	if(maxDepth <= currentPathLength):
		return False , None , numExploredStates , numUniqueExploredStates

	# Because of starting state the second condition must be > instead of >=
	if ( (curState.getHash() in dfsExplored and currentPathLength >= dfsExploredLengths[curState.getHash()]) or 
		 (curState.getHash() in allExplored and currentPathLength > allExploredBestLengths[curState.getHash()]) ):
		
		return False , None , numExploredStates , numUniqueExploredStates

	if(curState.getHash() not in dfsExplored and curState.getHash() not in allExplored):
		numUniqueExploredStates += 1

	allExplored.add(curState.getHash()); allExploredBestLengths[curState.getHash()] = currentPathLength
	dfsExplored.add(curState.getHash()); dfsExploredLengths[curState.getHash()] = currentPathLength

	placeBall(maze , curState , ballsDestLocs)
	possibleNewState = grabBall(maze , curState , ballsInitLocs , ballsDestLocs)

	if(possibleNewState is not None):
		result , resultState , numExploredStates , numUniqueExploredStates = DFS(possibleNewState , maxDepth ,
																				 currentPathLength , allExplored ,
																				 allExploredBestLengths , dfsExplored ,
																				 dfsExploredLengths , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates);
		if(result):
			return result , resultState , numExploredStates , numUniqueExploredStates


	if(isValidInMaze(maze , curState.getCurLoc_x() , curState.getCurLoc_y() - 1 , num_rows , num_columns)): # Left
		newState = State(curState.getCurLoc_x() , curState.getCurLoc_y() - 1 , curState.getCurCapacity() ,
						 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
						 curState)

		result , resultState , numExploredStates , numUniqueExploredStates = DFS(newState , maxDepth ,
																				 currentPathLength + 1 , allExplored ,
																				 allExploredBestLengths , dfsExplored ,
																				 dfsExploredLengths , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates)
		if(result):
			return result , resultState , numExploredStates , numUniqueExploredStates

	if(isValidInMaze(maze , curState.getCurLoc_x() + 1 , curState.getCurLoc_y() , num_rows , num_columns)): # Down
		newState = State(curState.getCurLoc_x() + 1 , curState.getCurLoc_y() , curState.getCurCapacity() ,
						 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
						 curState)

		result , resultState , numExploredStates , numUniqueExploredStates = DFS(newState , maxDepth ,
																				 currentPathLength + 1 , allExplored ,
																				 allExploredBestLengths , dfsExplored ,
																				 dfsExploredLengths , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates)
		if(result):
			return result , resultState , numExploredStates , numUniqueExploredStates

	if(isValidInMaze(maze , curState.getCurLoc_x() - 1 , curState.getCurLoc_y() , num_rows , num_columns)): # Up
		newState = State(curState.getCurLoc_x() - 1 , curState.getCurLoc_y() , curState.getCurCapacity() ,
						 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
						 curState)

		result , resultState , numExploredStates , numUniqueExploredStates = DFS(newState , maxDepth ,
																				 currentPathLength + 1 , allExplored ,
																				 allExploredBestLengths , dfsExplored ,
																				 dfsExploredLengths , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates)
		if(result):
			return result , resultState , numExploredStates , numUniqueExploredStates

	if(isValidInMaze(maze , curState.getCurLoc_x() , curState.getCurLoc_y() + 1 , num_rows , num_columns)): # Right
		newState = State(curState.getCurLoc_x() , curState.getCurLoc_y() + 1 , curState.getCurCapacity() ,
						 curState.getCurNumRemainingBalls() , curState.getNeedDelivery() , curState.getHasPicked() ,
						 curState)

		result , resultState , numExploredStates , numUniqueExploredStates = DFS(newState , maxDepth ,
																				 currentPathLength + 1 , allExplored ,
																				 allExploredBestLengths , dfsExplored ,
																				 dfsExploredLengths , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates)
		if(result):
			return result , resultState , numExploredStates , numUniqueExploredStates


	return False , None , numExploredStates , numUniqueExploredStates



def IDS(maze , num_rows , num_columns , start_x , start_y , goal_x , goal_y , capacity , num_balls , ballsInitLocs ,
		ballsDestLocs):
	
	idsMaxDepth = 1
	allExplored = set(); allExploredBestLengths = {}
	result = False
	numExploredStates = 0; numUniqueExploredStates = 0

	start_state = State(start_x , start_y , capacity , num_balls , [] , [])

	while(not result):
		result , resultState , numExploredStates , numUniqueExploredStates = DFS(start_state , idsMaxDepth ,
																				 0 , allExplored ,
																				 allExploredBestLengths , set() ,
																				 {} , maze , num_rows ,
																				 num_columns , numExploredStates ,
																				 numUniqueExploredStates)
		idsMaxDepth += 1

	return resultState , numExploredStates , numUniqueExploredStates


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
	goalState , numExploredStates , numUniqueExploredStates = IDS(maze , num_rows , num_columns , start_x , start_y ,
																  goal_x , goal_y , capacity , num_balls , ballsInitLocs ,
																  ballsDestLocs)
	toc = time.time()


	num_levels = getNumAndPrintActions(goalState)

	print("Num of levels: " + str(num_levels))
	print("Number of explored States: " + str(numExploredStates))
	print("Number of unique explored States: " + str(numUniqueExploredStates))
	print("Time: " + str(toc - tic) + " s")
	print("==============")