import math as m 

filename = r'C:\Users\44797\Downloads\weighted.csv'

def calculateFrequencies(responses):
    '''Calculates frequencies for response'''
    frequencies = {}
    for response in responses:
        if response in frequencies.keys():
            frequencies[response] +=1
        else:
            frequencies[response] = 1
    return frequencies

def calculateWeightedFrequencies(responses):
    '''Calculates weighted frequencies for response'''
    weightedFrequencies = {}
    for x, y in list(zip(weights, responses)):
        if y in weightedFrequencies.keys():
            weightedFrequencies[y] += x
        else:
            weightedFrequencies[y] = x
    return weightedFrequencies

def mean(responses):
    '''Calculates mean of responses in a list'''
    return sum(responses)/len(responses)

def weightedResponses(responses):
    '''Calculates weighted mean of responses in a list'''
    weightedResponses = []
    for x, y in list(zip(weights, responses)):
        weightedResponses.append(x*y)
    return weightedResponses

def weightedMean(responses):
    '''Calculates weighted mean of responses in a list'''
    return sum(weightedResponses(responses))/sum(weights)
   
def standardDeviation(responses):
    '''Calculates standard deviation of responses in a list'''
    deviations =\
    [(response - mean(responses)) ** 2 for response in responses]
    variance = (sum(deviations)/(len(deviations)))
    return m.sqrt(variance)

def weightedStandardDeviation(responses):
    '''Calculates standard deviation of responses in a list'''
    a = list(zip(weights, responses))
    deviations = [x*(y - weightedMean(responses))**2 for x, y in a]
    variance = (sum(deviations)/(sum(weights)))
    return m.sqrt(variance)

def crossTabulateFrequencies(responses1, responses2):
    '''Cross-tabulates 2 responses and returns frequencies'''
    crossTabulationResponses = list(zip(responses1, responses2))
    return calculateFrequencies(crossTabulationResponses)

def crossTabulateWeightedFrequencies(responses1, responses2):
    crossTabulationResponses = list(zip(responses1, responses2))
    return calculateWeightedFrequencies(crossTabulationResponses)

def crossTabulateMeans(responses1, responses2, responses3):
    '''Cross-tabulates 2 responses and returns means of 3rd response'''
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

    means = []
    for x,y in frequencySums:
        means.append(x/y)

    return dict(zip(means, list(zip(responses1, responses2))))

def crossTabulateWeightedMeans(responses1, responses2, responses3):
    '''Cross-tabulates 2 responses and returns weighted means of 3rd response'''
    crossTabulationWeightedFrequencies = \
    crossTabulateWeightedFrequencies(responses1, responses2)
    
    crossTabulationResponses = \
    list(zip(weights, responses1, responses2, responses3))
    crossTabulationWeightedSums = {}
    
    for w, x, y, z in crossTabulationResponses:
        if (x, y) in crossTabulationWeightedSums.keys():
            crossTabulationWeightedSums[(x,y)] += w*z
        else:
            crossTabulationWeightedSums[(x,y)] = w*z

    frequencySums = list\
    (zip(crossTabulationWeightedSums.values(),\
    crossTabulationWeightedFrequencies.values()))

    means = []
    for x, y in frequencySums:
        means.append(x/y)

    return dict(zip(means, list(zip(responses1, responses2))))

def printFrequencies(responses):
    '''Prints frequencies for response'''
    frequencies = calculateFrequencies(responses)
    for k, v in sorted(frequencies.items()):
        print(f'{k}: {v}')

def printWeightedFrequencies(responses):
    weightedFrequencies = calculateWeightedFrequencies(responses)
    for k, v in sorted(weightedFrequencies.items()):
        print(f'{k}: {v}')

def printDescriptives(responses):
    '''Gets descriptive statistics for responses'''
    print(f'min: {min(responses)}')
    print(f'max: {max(responses)}')
    print(f'mean: {mean(responses)}')
    print(f'standard deviation: {standardDeviation(responses)}')

def printWeightedDescriptives(responses):
    '''Gets weighted descriptive statistics for responses'''
    print(f'min: {min(responses)}')
    print(f'max: {max(responses)}')
    print(f'weighted mean: {weightedMean(responses)}')
    print('weighted standard deviation: '\
    f'{weightedStandardDeviation(responses)}')

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

def printWeightedCrossTabulations(responses1, responses2, responses3):
    '''Formats and prints weighted cross-tabulation results'''
    crossTabulationWeightedFrequencies = \
    crossTabulateWeightedFrequencies(responses1, responses2)

    crossTabulationWeightedMeans = \
    crossTabulateWeightedMeans (responses1, responses2, responses3)

    fullWeightedCrossTabulation = \
    list(zip(crossTabulationWeightedFrequencies.keys(),\
    crossTabulationWeightedFrequencies.values(),\
    crossTabulationWeightedMeans))

    for x,y,z in sorted(fullWeightedCrossTabulation): 
        print(f'{x}: frequency = {y}, mean age = {z}')

#Creates lists for each data column (and extra list for age bins)
serials = []
weights = []
genders = []
ages = []
ageBins = []
deodorantUses = []

#Splits data in csv rows and appends each column to respective list
with open(filename) as f:
    next(f)
    for row in f:
        x = row.strip().split(',')
        serials.append(x[0])
        weights.append(float(x[1]))
        genders.append(x[2])
        ages.append(int(x[3]))
        deodorantUses.append(x[4])

#Categorises ages into age bins and appends these to age bins list
for i in range(len(ages)):
    ageBins.append(m.floor((ages[i]-1)/10))

#Performs analyses on data and prints results
print('UN-WEIGHTED RESULTS')
print('Actual Gender Frequencies:')
printFrequencies(genders)

print('\nDeodorant Use Frequencies:')
printFrequencies(deodorantUses)

print('\nAge Descriptives:')
printDescriptives(ages)

print('\nAge Bin Frequencies (0 = 0-10, 1 = 11-20...):')
printFrequencies(ageBins) 

print('\nCross-Tabulation with Frequencies and Mean Ages'\
' (Gender, Deodorant Use):')
printCrossTabulations(genders, deodorantUses, ages)

print('\nWEIGHTED RESULTS')
print('Weighted Gender Frequencies:')
printWeightedFrequencies(genders)

print('\nWeighted Age Bin Frequencies (0 = 0-10, 1 = 11-20...):')
printWeightedFrequencies(ageBins)

print('\nWeighted Age Descriptives:')
printWeightedDescriptives(ages)

print('\nCross-Tabulation with Weighted Frequencies and Mean Ages'\
' (Gender, Deodorant Use):')
printWeightedCrossTabulations(genders,deodorantUses,ages)
