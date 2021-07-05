import pprint, math as m, pyodbc

def calcFrequencies(responses):
    '''Calculates frequencies for responses in a given 'column' '''
    frequencies = {}

    for response in responses:
        if response in frequencies.keys():
            frequencies[response] += 1
        else:
            frequencies[response] = 1

    return frequencies

def crosstab(*responses):
	'''crosstabs columns of responses'''
	return calcFrequencies(list(zip(*responses)))

def aggregateCrosstabFrequencies(index):
	'''Aggregates frequencies of responses for each 'column' in a crosstab'''
	frequencies = {}

	for t, frequency in currentCrosstab.items():

		if t[index] in frequencies.keys():
			frequencies[t[index]] += frequency
		else:
			frequencies[t[index]] = frequency

	return dict(sorted(frequencies.items()))

def frequenciesDifference(currentFrequencies, desiredFrequencies):
	'''Calculates total difference between current and desired frequencies'''
	totalDiff = 0

	for currentFrequency, desiredFrequency in\
		zip(currentFrequencies.values(), desiredFrequencies.values()):
		totalDiff += abs(currentFrequency - desiredFrequency)

	return totalDiff

def calcDifferencePerCase(currentFrequencies, desiredFrequencies):
	'''Calculates total difference between current and desired frequencies 
	per case (this is used to check whether to perform another iteration)'''
	difference = frequenciesDifference(currentFrequencies, desiredFrequencies)
	sampleSize = sum(actualCrosstab.values())
	return difference / sampleSize

def calcWeights(currentFrequencies, desiredFrequencies):
	'''Calculates weight factors as df/cf quotient'''
	weights = []

	for currentFrequency, desiredFrequency in\
		zip(currentFrequencies.values(), desiredFrequencies.values()):
		weights.append(desiredFrequency/currentFrequency)

	return weights

def applyWeights(index):
	'''applies weights to 'column'(index in tuple) in current crosstab'''
	for k, v in currentCrosstab.items():
		v = v*weights[int(k[index])-1]
		currentCrosstab[k] = v

class RimColumn():
	''' Represents columns to be used in RIM Weighting'''
	numOfRimColumns = 0

	def __init__ (self, column, desiredFrequencies):
		rimColumns.append(self)
		columns.append(column)
		self.index = RimColumn.numOfRimColumns
		self.column = column
		self.actualFrequencies = calcFrequencies(column)
		self.currentFrequencies = self.actualFrequencies
		self.desiredFrequencies = desiredFrequencies
		RimColumn.numOfRimColumns +=1

rimColumns = []
columns = []

#Connects to SQL Server Database and retrieves data
connection = pyodbc.connect('Driver={SQL Server};'
					        'Server=.\sqlexpress;'
					        'Database=Nivea;'
					        'Trusted_connection=yes')

cursor = connection.cursor()
cursor.execute('SELECT * FROM Nivea.dbo.weighted_custom')

data = []
for row in cursor:
	data.append(row[6])

#Creates list for each 'column'
genders = []
ages = []
ageBins = []
deodorantUses = []

#Separates data by 'column' and appends these to respective 'column' lists
for i in data:
	x = i.split('&')

	for i in x:
		if 'Qs0' in i:
			genders.append(i.replace('Qs0=',''))
		elif 'Qs1_1' in i:
			ages.append(int(i.replace('Qs1_1=','')))
		elif 'Qs3' in i:
			deodorantUses.append(i.replace('Qs3=',''))

#Splits age data into age bins
for i in range(len(ages)):
    ageBins.append(m.floor((ages[i]-1)/10))

#Arbitrary desired frequency distributions
desiredAgeFrequencies = \
{'1':75, '2':400, '3':500, '4':300, '5':200, '6':29, '7':1}

desiredGenderFrequencies = \
{'1':700, '2':805}

#Creates Rim Columns for Columns to be used in rim weighting algorithm 
ageRimColumn = RimColumn(ageBins, desiredAgeFrequencies)
genderRimColumn = RimColumn(genders, desiredGenderFrequencies)

#Assigns actual and an initial current crosstab
actualCrosstab = crosstab(*columns)
currentCrosstab = crosstab(*columns)

#Assigns initial total difference between actual and desired freq per 
totalDiffPerCase = 0
for rimColumn in rimColumns:
	totalDiffPerCase += \
	calcDifferencePerCase(rimColumn.currentFrequencies,\
						  rimColumn.desiredFrequencies)

# RIM-Weighting Algorithm
iteration = 0
while totalDiffPerCase > 0.00000000000000001:
	totalDiffPerCase = 0

	#Calculates and applies weights to crosstab frequencies
	for rimColumn in rimColumns:
		weights = \
		calcWeights(rimColumn.currentFrequencies,rimColumn.desiredFrequencies)

		applyWeights(rimColumn.index)

		#Updates current freq to reflect newly weighted crosstab freq
		for rimColumn in rimColumns:
			rimColumn.currentFrequencies =\
			aggregateCrosstabFrequencies(rimColumn.index)

	#Calculates total difference per case at end of iteration
	for rimColumn in rimColumns:
		totalDiffPerCase += \
		calcDifferencePerCase(rimColumn.currentFrequencies,\
							  rimColumn.desiredFrequencies)
		
	#Increases iteration and prints current iteration and difference per case
	iteration +=1
	print(f'\niteration: {iteration} \ntotal difference per case between '\
		  f'actual and desired frequencies: {totalDiffPerCase}')

#Caclulates weights based on difference between actual and current crosstab freq
weights = calcWeights(actualCrosstab, currentCrosstab)

#Prints weights paired with corresponding crosstab key
crosstabWithWeights = dict(sorted(zip(actualCrosstab.keys(), weights)))
print(f'\nWeights calculated after {iteration} iterations:')
pprint.pprint(crosstabWithWeights)