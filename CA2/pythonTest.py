import time
import random
import bisect

class JobScheduler:
    def __init__(self, fileInfo):
        self.days = fileInfo[0]
        self.doctors = len(fileInfo[1])
        self.doctorsIds = fileInfo[1]
        self.maxCapacity = fileInfo[2]
        self.allShifts = fileInfo[3]
        self.popSize = 300
        # [[[]] , [[] ==> gene(shift)] ==> chromosome(one assignment)] ==> chromosomes(all assignments)
        self.chromosomes = self.generateInitialPopulation()
        self.elitismPercentage = 0.18
        self.pc = 0.9
        self.pm = 0.1
#         self.crossOverPoints = -1
        self.bestFitness = float("inf")
        self.repetitaveFitnesses = 0
        
    def createOneGene(self):
        num_docs = random.randint(0 , self.doctors)
        visited_docs = [False] * self.doctors
        gene = []
        
        for _ in range(num_docs):
            doc_ID = random.randint(0 , self.doctors - 1)
            while(visited_docs[doc_ID]):
                doc_ID = random.randint(0 , self.doctors - 1)
            
            gene.append(doc_ID)
            visited_docs[doc_ID] = True
            
        return gene
    
    
    def generateInitialPopulation(self):
        chromosomes_list = []
        for _ in range(self.popSize):
            chromosome = []
            for _ in range(self.days * 3):
                chromosome.append(self.createOneGene())
            chromosomes_list.append(chromosome)
            
        return chromosomes_list;
        
    
    def crossOver(self, chromosome1, chromosome2):
        if(random.random() <= self.pc):
            # # One-point
            # slice_point = random.randint(0 , len(chromosome1) - 1)
            # return (chromosome1[0 : slice_point] + chromosome2[slice_point:] ,
            #         chromosome2[0 : slice_point] + chromosome1[slice_point:])


            # Two-point
            slice_point_1 = random.randint(0 , len(chromosome1) - 1)
            slice_point_2 = random.randint(slice_point_1 , len(chromosome1) - 1)
            return (chromosome1[0 : slice_point_1] + chromosome2[slice_point_1 : slice_point_2] + chromosome1[slice_point_2:] ,
                    chromosome2[0 : slice_point_1] + chromosome1[slice_point_1 : slice_point_2] + chromosome2[slice_point_2:])

            # # Three-point
            # slice_point_1 = random.randint(0 , len(chromosome1) - 1)
            # slice_point_2 = random.randint(slice_point_1 , len(chromosome1) - 1)
            # slice_point_3 = random.randint(slice_point_2 , len(chromosome1) - 1)
            # return (chromosome1[0 : slice_point_1] + chromosome2[slice_point_1 : slice_point_2] + chromosome1[slice_point_2 : slice_point_3] + chromosome2[slice_point_3:] ,
            #         chromosome2[0 : slice_point_1] + chromosome1[slice_point_1 : slice_point_2] + chromosome2[slice_point_2 : slice_point_3] + chromosome1[slice_point_3:])            
        
        return chromosome1 , chromosome2
    
    
    def mutate_gene(self , gene):
        existing_docs = [False] * self.doctors
        
        for docID in gene:
            existing_docs[docID] = True
        
        if(False not in existing_docs):
            return gene
        
        if(random.random() <= 0.75):

            has_mutated_docs = [False] * len(gene)
            num_toBeMutated = 0
            
            if(len(gene) > 0):
                if(self.doctors - len(gene) < len(gene)):
                    num_toBeMutated = random.randint(1 , self.doctors - len(gene))
                else:
                    num_toBeMutated = random.randint(1 , len(gene))
            
            for _ in range(num_toBeMutated):
                index_toBeMutated = random.randint(0 , len(gene) - 1)
                while(has_mutated_docs[index_toBeMutated]):
                    index_toBeMutated = random.randint(0 , len(gene) - 1)
                has_mutated_docs[index_toBeMutated] = True
                
                new_docID = existing_docs.index(False)
                existing_docs[new_docID] = True
                existing_docs[gene[index_toBeMutated]] = False
                
                gene[index_toBeMutated] = new_docID

        else:
            new_gene = []

            for docID in self.doctorsIds:
                if(not existing_docs[docID]):
                    new_gene.append(docID)

            gene = new_gene            
            
        # if(num_toBeMutated == 0):
        #     gene = self.createOneGene()
        
        return gene
    
                
    def mutate(self, chromosome):
        if(random.random() <= self.pm):
            num_toBeMutated = random.randint(0 , len(chromosome) - 1)  # change at least 50% of shifts
            visited_shifts = [False] * len(chromosome)
            for i in range(num_toBeMutated):
                index_toBeMutated = random.randint(0 , len(chromosome) - 1)
                while(visited_shifts[index_toBeMutated]):
                    index_toBeMutated = random.randint(0 , len(chromosome) - 1)            
                visited_shifts[index_toBeMutated] = True
                
                chromosome[index_toBeMutated] = self.mutate_gene(chromosome[index_toBeMutated])

                # # CAN GIVE IT MORE THOUGHT
                # if(i < num_toBeMutated // 2):
                #     chromosome[index_toBeMutated] = self.mutate_gene(chromosome[index_toBeMutated])
                # else:
                #     chromosome[index_toBeMutated] = chromosome[index_toBeMutated][0:len(chromosome[index_toBeMutated]) // 2]
             
        return chromosome
        
        
    def checkShiftConstraints(self , chromosome , nightIndex):
        num_conflicts = 0
        for doc in chromosome[nightIndex]:
            if(doc in chromosome[nightIndex + 1]): # Tomorrow morning
                num_conflicts += 1
            
            if(doc in chromosome[nightIndex + 2]): # Tomorrow evening
                num_conflicts += 1
                
            if(doc in chromosome[nightIndex + 3]): # Three night shifts in a row
                if(nightIndex + 6 < len(chromosome) and doc in chromosome[nightIndex + 6]):
                    num_conflicts += 1

        return num_conflicts
    

    def checkCapacityAndRangeConstraints(self , chromosome , doc_id , fitness):
        num_shifts = 0
        for i in range(len(chromosome)):
            shift = chromosome[i]
            
            if(doc_id in shift):
                num_shifts += 1
            
            # Range Constraints
            if(doc_id == 0):
                if(len(shift) < self.allShifts[i // 3][i % 3][0]):
                    fitness += (self.allShifts[i // 3][i % 3][0] - len(shift))
                elif(len(shift) > self.allShifts[i // 3][i % 3][1]):
                    fitness += (len(shift) - self.allShifts[i // 3][i % 3][1])
                

        if(num_shifts > self.maxCapacity):
            fitness += 1

        return fitness
                
                
    def calculateFitness(self, chromosome):
        fitness = 0
        for nightIndex in range(2 , len(chromosome) - 1 , 3):
            fitness += self.checkShiftConstraints(chromosome , nightIndex)
                
        for doc_id in self.doctorsIds:
            fitness = self.checkCapacityAndRangeConstraints(chromosome , doc_id , fitness)
        
        
        return fitness
    
    
    def getTwoParentsForCrossOver(self , chromosomes , fitnesses , max_fitness):
        probability = []
        for i in range(len(fitnesses)):
            probability += ([i] * (max_fitness - fitnesses[i] + 1))
        
        # print(probability)
        
        idx_1 = random.randint(0 , len(probability) - 1)
        idx_2 = random.randint(0 , len(probability) - 1)
        while(idx_1 == idx_2):
            idx_2 = random.randint(0 , len(probability) - 1)

        # print(probability[idx_1])
        # print(probability[idx_2])
        # print("=============")
        return chromosomes[probability[idx_1]] , chromosomes[probability[idx_2]]
    
    
    def generateNewPopulation(self):
        new_generation = []
        sortedChromosomes = []
        fitnesses = [];
        for i in range(self.popSize):
            chromosome = self.chromosomes[i]
            current_fitness = self.calculateFitness(chromosome)
            idx = bisect.bisect(fitnesses , current_fitness)
            fitnesses.insert(idx , current_fitness)
            sortedChromosomes.insert(idx , chromosome)
        
        fitnesses = fitnesses[::-1]
        sortedChromosomes = sortedChromosomes[::-1]
        max_fitness = fitnesses[0]
        # print(fitnesses)
        # print("=========")
        
        # elitism        
        for _ in range(int(self.elitismPercentage * self.popSize)):
            new_generation.append(sortedChromosomes.pop())
            fitnesses.pop()
        
        # Crossover
        for _ in range(len(sortedChromosomes) // 2):
            parent_1 , parent_2 = self.getTwoParentsForCrossOver(sortedChromosomes , fitnesses , max_fitness);
            child_1 , child_2 = self.crossOver(parent_1 , parent_2)
            new_generation.append(self.mutate(child_1))
            new_generation.append(self.mutate(child_2))
            
        return new_generation
    
    def hasReachedGoal(self):
        prevBestFitness = self.bestFitness
        for chromosome in self.chromosomes:
            current_fitness = self.calculateFitness(chromosome)
            if(current_fitness < self.bestFitness):
                self.bestFitness = current_fitness
                # ch = chromosome
                
            if(current_fitness == 0):
                return chromosome

        print(self.bestFitness)
        # print("bestFitness: " + str(self.bestFitness))
        # print("prevBestFitness: " + str(prevBestFitness))
        # print(ch)
        # print("pm: " + str(self.pm))
        # print("repetitaveFitnesses: " + str(self.repetitaveFitnesses))
        if(prevBestFitness == self.bestFitness):
            self.repetitaveFitnesses += 1
        else:
            self.repetitaveFitnesses = 0

        if(self.repetitaveFitnesses == 50):
            self.pm = 0
            self.pc = 1

        return None
    
    def schedule(self):
        while(self.hasReachedGoal() is None):
            self.chromosomes = self.generateNewPopulation()
        
        return self.chromosomes



def readInput(testFile) :
    file = open(testFile, 'r+')
    fileList = file.readlines()
    fileList = [s.replace('\n', '') for s in fileList]
    
    [days, doctors] = [int(i) for i in fileList[0].split()]
    maxCapacity = int(fileList[1])
    
    allShifts = []
    for i in range(2, days + 2):
        dayRequirements = fileList[i].split()
        morningReqs = [int(i) for i in dayRequirements[0].split(",")]
        eveningReqs = [int(i) for i in dayRequirements[1].split(",")]
        nightReqs = [int(i) for i in dayRequirements[2].split(",")]
        
        allShifts.append((morningReqs, eveningReqs, nightReqs))

    file.close()
    return [days, list(range(doctors)), maxCapacity, allShifts]

testFile1 = "test1.txt"
testFile2 = "test2.txt"

fileInfo1 = readInput(testFile1)

start = time.time()

scheduler = JobScheduler(fileInfo1)
scheduler.schedule()

end = time.time()

print("test 1: ", '%.2f'%(end - start), 'sec')