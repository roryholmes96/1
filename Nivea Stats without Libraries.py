filename = \
r'C:\Users\44797\Downloads\4943-21 Nivea Adcepts Brazil0_21060704.csv'

#Defines functions to perform various statistical analyses
def calculateFrequencies(responses):
    '''Calculates frequencies for variable'''
    frequencies = {}
    for variable in responses:
        if variable in frequencies.keys():
            frequencies[variable] +=1
        else:
            frequencies[variable] = 1
    return frequencies

def mean(responses):
    '''Calculates mean of a variable'''
    return sum(responses)/len(responses)
   
def standardDeviation(responses):
    '''Calculates standard deviation of a variable'''
    deviations =\
    [(variable - mean(responses)) ** 2 for variable in responses]
    variance = (sum(deviations)/(len(deviations)))
    standardDeviation = variance** (1/2)
    return standardDeviation

def crossTabulateFrequencies(responses1, responses2):
    '''Cross-tabulates 2 variables and returns frequencies'''
    crossTabulationResponses = list(zip(responses1, responses2))
    crossTabulationFrequencies = {}
    for t in crossTabulationResponses:
        if t in crossTabulationFrequencies.keys():
            crossTabulationFrequencies[t] +=1
        else:
            crossTabulationFrequencies[t] =1
    return(crossTabulationFrequencies)

def crossTabulateMeans(responses1, responses2, responses3):
    '''Cross-tabulates 2 variables and returns means of 3rd variable'''
    crossTabulationFrequencies = \
    crossTabulateFrequencies(responses1, responses2)
    
    crossTabulationResponses = \
    list(zip(responses1, responses2, responses3))
    crossTabulationSums = {}
    
    for x, y, z in crossTabulationResponses:
        if (x, y) in crossTabulationSums.keys():
            crossTabulationSums[(x,y)] += z
        else:
            crossTabulationSums[(x,y)] = z

    frequencySums = list\
    (zip(crossTabulationSums.values(),crossTabulationFrequencies.values()))

    crossTabulationMeans = []
    for x,y in frequencySums:
        crossTabulationMeans.append(x/y)

    return crossTabulationMeans

def printFrequencies(responses):
    '''Prints frequencies for variable'''
    frequencies = calculateFrequencies(responses)
    for k, v in sorted(frequencies.items()):
        print(f'{k}: {v}')

def printDescriptives(responses):
    '''Gets descriptive statistics for variable'''
    print(f'min: {min(responses)}')
    print(f'max: {max(responses)}')
    print(f'mean: {mean(responses)}')
    print(f'standard deviation: {standardDeviation(responses)}')

def printCrossTabulations(responses1, responses2, responses3):
    '''Formats and prints cross-tabulation results'''
    crossTabulationFrequencies = \
    crossTabulateFrequencies(responses1, responses2)

    crossTabulationMeans = \
    crossTabulateMeans (responses1, responses2, responses3)

    fullCrossTabulation = list(zip(crossTabulationFrequencies.keys(),\
    crossTabulationFrequencies.values(),\
    crossTabulationMeans))

    for x,y,z in sorted(fullCrossTabulation): 
        print(f'{x}: frequency = {y}, mean age = {z}')

#Creates lists for each data column (and extra list for age bins)
serials = []
genders = []
ages = []
ageBins = []
deoderantUses = []

#Splits data in csv rows and appends each column to respective list
with open(filename) as f:
    next(f)
    for row in f:
        x = row.strip().split(',')
        serials.append(x[0])
        genders.append(x[1])
        ages.append(int(x[2]))
        deoderantUses.append(x[3])

#Categorises ages into age bins and appends these to age bins list
for i in range(len(ages)):
    if ages[i] < 11:
        ageBins.append('age_0_10')
    elif ages[i] < 21:
        ageBins.append('age_11_20')
    elif ages[i] < 31:
        ageBins.append('age_21_30')    
    elif ages[i] < 41:
        ageBins.append('age_31_40')
    elif ages[i] < 51:
        ageBins.append('age_41_50')
    elif ages[i] < 61:
        ageBins.append('age_51_60')
    elif ages[i] < 71:
        ageBins.append('age_61_70')
    elif ages[i] < 81:
        ageBins.append('age_71_80')

#Performs analyses on data and prints results
print('Gender Frequencies:')
printFrequencies(genders)

print('\nDeoderant Use Frequencies:')
printFrequencies(deoderantUses)

print('\nAge Descriptives:')
printDescriptives(ages)

print('\nAge Bin Frequencies:')
printFrequencies(ageBins) 

print('\nCross-Tabulation with Frequencies and Mean Age'\
' (Gender, Deoderant Use):')
printCrossTabulations(genders, deoderantUses, ages)
