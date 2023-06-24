"""Efficient utilization of space using Genetic Algorithm"""

#%% 
import numpy as np
import random
#Generates parent chromosomes having count=population
#'size' contains no. of files
def generateParents(size,population):     
    parents = np.array(random.randint(0, 2**size - 1))   #produces random number b/w 0 and 2^size
    for i in range(1, population):
        parents = np.append(parents, random.randint(0, 2**size - 1))
    #print(parents)
    return parents                        #returns parent chromosomes

#%% 
def totalSize(data, size):          #gets the total size of files placed at the indexes mentioned in the 'data' chromosome
    s = 0
    for i in range(0, size-1):
        if(data & (1 << i) > 0):    #returns TRUE when the bit at 'i th' position in 'data' chromosome is 1 
            s += file_sizes[i]
    return s                        #returns the total size
#%% 
def reduceSize(rec, size):          #reduces the size of 'rec' chromosome till the size gets less than 700
    while totalSize(rec, size) > 700:
        index = random.randint(0, size - 1)      #generates a random 'index' whose bit is to be set to 0 in 'rec' chromosome
        if(rec & (1 << index) > 0):              #checks if the bit at 'index' position is '1'
            rec = rec ^ (1 << index)             #changes the bit at 'index' to 0
    return rec                                   #returns the transformed 'rec' chromosome

#%% 
#sets the size of the chromosomes to less than 700 and assigns fitness to each of the chromosomes 
#'data' array carries the chromosomes;'size' contains no. of files ;'population' contains no. of chromosomes to be returned
def fixChromosomes(data, size, population):      
    datasize = data.shape[0]                     #gives the shape of the array 'data'
    fitness = np.zeros((datasize,1), dtype=int)  #initialize 'fitness' to 0 for all the chromosomes
    for i in range(0, datasize):
        rec = data[i]
        if(totalSize(rec, size) > 700):          
            rec = reduceSize(rec, size)          #reduces the size of the chromosome to less than 700
            data[i] = rec
        fitness[i] = -1* totalSize(data[i], size)  #assigns fitness to the chromosome based on the space it occupies
    data = np.transpose(np.array([data]))
    generation = np.concatenate((data, fitness), axis=1)  #concatenates the 'data' and 'fitness' arrays column-wise
    generation = generation[generation[:population, 1].argsort()]  #sorts the 'generation' array w.r.t. 'fitness'
    return generation                             #returns the 2-D 'generation' array
#%% 
def mutate(rec, size):                           #mutates a random bit of 'rec' to 0 or 1
    index = random.randint(0, size - 1)          #generates a random 'index' b/w 0 and 'size' of 'rec' 
    rec = rec ^ (1 << index)                     #mutates the bit
    return rec                                   #returns the mutated chromosome
#%% 
def crossover(mom, dad, size):                              #crosses over the 2 parents to generate 2 offsprings
    index = random.randint(1, size - 1)                     #gets random 'index' around which the crossover will take place
    mom1 = mom & (2**index -1)                              #selects the rightmost 'index' no. of bits from 'mom' chromosome 
    mom2 = mom & ((2**(size-index) -1) << index)            #selects the rest leftmost bits from the 'mom' chromosome
    dad1 = dad & (2**index -1)                              #selects the rightmost 'index' no. of bits from 'dad' chromosome 
    dad2 = dad & ((2**(size-index) -1) << index)            #selects the rest leftmost bits from the 'dad' chromosome
    return mutate(mom1|dad2, size), mutate(dad1|mom2, size) #mutates the two offspring and returns them
#%% 
def newGeneration(generation, size):             #generates the new generation using the parents
    top4 = generation[:4, 0]                     #selects top 4 chromosomes from the previous generation based on fitness
    newGen = generation[:2,0]                    #adds the top 2 chromosomes from the previous generation to the new generation
    for i in range(0, 4):                        #mating each of the top 4 chromosomes with each other
        for j in range(0, 4):
            if(i != j):
                c1, c2 = crossover(top4[i], top4[j], size)   #each crossover gives 2 offsprings
                newGen = np.append(newGen, c1)               #the offspring are added to the new generation
                newGen = np.append(newGen, c2)
                #print(newGen)
    return newGen                              #returns the new generation containing all the new chromosomes
#%% 
#uses the genetic algorithm to obtain the no. of CDs ; (each of size 700) to store 'file_cnt' of files
def implement_ga(file_cnt, file_sizes, population, generationsPerCD):   
    curCD = 1                                            #current CD
    combinedSizes = totalSize(2**file_cnt-1, file_cnt)       #total size of all the files
    print("Total size of all files: ", combinedSizes)
    doneSizes = 0.0                                      #contains the data size stored in CDs yet
    while(True):                                         #runs till all the files have not been stored
        if(file_cnt == 0):
            break
        parents = generateParents(file_cnt,population)     #generates parents having count=population
        generation = fixChromosomes(parents, file_cnt, population)  #fixing and assigning fitness to chromosomes
        ng = generation
        for i in range(generationsPerCD):                #new generations are produced 'generationsPerCD' times
            ng = newGeneration(ng, file_cnt)               
            ng = fixChromosomes(ng, file_cnt, population)
        allFileSize = totalSize(2**file_cnt-1, file_cnt)     #size of all the available files
        cdContents = ng[0,0]                             #choosing the best chromosome from the final generation
        if(allFileSize < 700):                           #for the last iteration
            cdContents = 2**file_cnt -1                    #all the last available files will be put into the last CD
        currentBestCDSize = totalSize(cdContents, file_cnt)      #size of the best chromosome
        
        #returns TRUE only if the best chromosome has a size b/w 699 and 700 OR for the last batch of files
        if(currentBestCDSize >= 699 or allFileSize < 700):     
            indexesToRemove = []                    #list to store the indexes of files to be put into the current CD
            for i in range(0, file_cnt):              
                if(cdContents & (1 << i) > 0):      #to check if the present bit of the best chromosome is 1
                    indexesToRemove.append(i)       
            indexesToRemove = list(reversed(indexesToRemove))      #the list is reversed
            doneSizes += currentBestCDSize                         #stores the total capacity stored till now in the CDs
            print("CD"+ str(curCD) + ": MP3 Count:" + str(len(indexesToRemove)) + " Size: " + str(currentBestCDSize))
            #print("Combined Size of all files stored yet: ",doneSizes)
            file_cnt = file_cnt - len(indexesToRemove)                 #updates the total no. of files 
            for i in range(len(indexesToRemove)):                  
                file_sizes = np.delete(file_sizes, indexesToRemove[i])         #deletes the files which have been stored in this iteration
            curCD = curCD + 1                                      #increments the CD number
        else:
            continue
#%%         
population = 10                           #count of initial population of chromosomes
file_cnt = 100                              #total number of files
generationsPerCD = 3                      #no. of iterations for producing offsprings
maxFileSize = 100                         #maximum file size
file_sizes = maxFileSize*np.random.rand(file_cnt, 1)    #assigning size(b/w 0 to 100) to each of the 100 files

implement_ga(file_cnt, file_sizes, population, generationsPerCD)
