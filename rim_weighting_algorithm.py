import pprint, math as m, pyodbc

def calcFrequencies(responses):
    '''Calculates the frequencies for each possible responses in a survey 
       variable's list of responses
    '''
    frequencies = {}

    for response in responses:
        if response in frequencies.keys():
            frequencies[response] += 1
        else:
            frequencies[response] = 1

    return dict(sorted(frequencies.items()))

def crosstab(*responses):
	'''Crosstabs the lists of responses for multiple survey variables. The
	   crosstab is a dictionary where there is a key for each possible 
	   combination of responses with the frequency of cases who responded this 
	   way as the value.
	'''
	return calcFrequencies(list(zip(*responses)))

def aggregateCrosstabFrequencies(index):
	'''Aggregates the frequencies of responses for each survey variable in a 
	   crosstab.
	'''
	frequencies = {}

	for t, frequency in currentCrosstab.items():

		if t[index] in frequencies.keys():
			frequencies[t[index]] += frequency
		else:
			frequencies[t[index]] = frequency

	return dict(sorted(frequencies.items()))

def frequenciesDiff(currentFrequencies, desiredFrequencies):
	'''Calculates the difference between current frequencies (i.e. the 
	   frequencies after current iteration of weighting) and desired frequencies 
	   for each possible response in a survey variable's responses
	'''
	totalDiff = 0

	for currentFrequency, desiredFrequency in\
		zip(currentFrequencies.values(), desiredFrequencies.values()):
		totalDiff += abs(currentFrequency - desiredFrequency)

	return totalDiff

def diffPerCase(currentFrequencies, desiredFrequencies):
	'''Calculates the total difference between current and desired frequencies 
	   for a given survey variable, divided by the number of respondents 
	   (this is used to check whether to perform another iteration)
	'''
	difference = frequenciesDiff(currentFrequencies, desiredFrequencies)
	sampleSize = sum(actualCrosstab.values())
	return difference / sampleSize

def calcWeights(currentFrequencies, desiredFrequencies):
	'''Calculates weights as desiredFrequencies/currentFrequencies quotient '''
	weights = []

	for currentFrequency, desiredFrequency in\
		zip(currentFrequencies.values(), desiredFrequencies.values()):
		weights.append(desiredFrequency/currentFrequency)

	return weights

def applyWeights(structureIndex, responseIndexes):
	'''Applies weights to the (current) frequencies of a given variable in the
	   current crosstab (i.e. the crosstab after current iteration of 
	   weighting). The structureIndex passed as an argument denotes the 
	   position of the survey  variable in the current crosstab's key tuple. For 
	   each item in the crosstab, this formula retrieves the value of the 
	   response (e.g. 78 for region 78). It then uses this value to get that 
	   response's index position in the ordered set of possible responses i.e. 
	   (0 if 78 is the lowest value in the set of region responses). This index 
	   position is retrieved from the responseIndexes passed as an argument; a 
	   dictionary with each possible response for a variable as keys, and it's 
	   index as the corresponding value. This response index is then used to
	   identify which values (frequencies) to apply which weights to in the 
	   current crosstab
	'''
	for k, v in currentCrosstab.items():
		response = k[structureIndex]
		responseIndex = responseIndexes[response]
		v = v*weights[responseIndex]
		currentCrosstab[k] = v

class RimVariable():
	''' Represents survey variables to be used in RIM Weighting'''
	def __init__ (self, responses, desiredFrequencies, structureIndex):
		self.actualFrequencies = calcFrequencies(responses)
		self.currentFrequencies = self.actualFrequencies
		self.desiredFrequencies = dict(sorted(desiredFrequencies.items()))
		self.structureIndex = structureIndex
		self.responseIndexes = dict((v,k) for k,v in \
							   dict(enumerate(self.actualFrequencies)).items())

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

#Creates list for the set of responses for each survey variable
genderResponses = []
ageResponses = []
ageResponsesBins = []
deodorantUseResponses = []

#Separates data by survey variable and appends these to the respective survey
#variable response lists
for i in data:
	x = i.split('&')

	for i in x:
		if 'Qs0' in i:
			genderResponses.append(i.replace('Qs0=',''))
		elif 'Qs1_1' in i:
			ageResponses.append(int(i.replace('Qs1_1=','')))
		elif 'Qs3' in i:
			deodorantUseResponses.append(i.replace('Qs3=',''))

#Splits age data into bins
for i in range(len(ageResponses)):
    ageResponsesBins.append(m.floor((ageResponses[i]-1)/10))

#Arbitrary desired frequency distributions
desiredAgeFrequencies = \
{'1':75, '2':400, '3':500, '4':300, '5':200, '6':29, '7':1}

desiredGenderFrequencies = \
{'1':700, '2':805}

#Creates list which contains the list of responses for each survey variable to
#be used in rim-weighting
surveyVariableResponses = [ageResponsesBins, genderResponses]

#Creates list which contains the frequency distribution dictonary for each 
#survey variable to be used in rim-weightin
desiredFrequencies = [desiredAgeFrequencies, desiredGenderFrequencies]

#Creates index list which contains the index (to be used in various functions) 
#for each item in surveyVariableResponses list
index = []
for t in list(enumerate(surveyVariableResponses)):
	index.append(t[0])

#Creates a structure to be used in loop which assigns objects to RimVariable
#class. Each item in the structure is a tuple containing survey variable's list
#of responses, the desired frequency distribution for that variable, and its 
#index position (this is the same in both this structure and the crosstab)
structure = list(zip(surveyVariableResponses, desiredFrequencies, index))

#Assigns actual and an initial current crosstab
actualCrosstab = crosstab(*surveyVariableResponses)
currentCrosstab = crosstab(*surveyVariableResponses)

#Creates a RimVariable instance for each variable to be used in the
#rim-weighting algorithm and appends it to rimVariables list
rimVariables = []
for surveyVariableResponses, desiredFrequencies, index in structure:
	rimVariable =RimVariable(surveyVariableResponses, desiredFrequencies, index)
	rimVariables.append(rimVariable)

#Assigns initial total difference between actual and desired freq per case for 
#all survey variables. i.e the sum of totalDiffPerCase for each survey variable
totalDiffPerCase = 0
for rimVariable in rimVariables:
	totalDiffPerCase += \
	diffPerCase(rimVariable.currentFrequencies,\
				rimVariable.desiredFrequencies)

# RIM-Weighting Algorithm
iteration = 0
while totalDiffPerCase > 0.00000000000000001 and iteration < 50:
	totalDiffPerCase = 0

	#Calculates and applies weights to crosstab frequencies
	for rimVariable in rimVariables:
		weights = \
		calcWeights(rimVariable.currentFrequencies,\
					rimVariable.desiredFrequencies)

		applyWeights(rimVariable.structureIndex, rimVariable.responseIndexes)

		#Updates current freq to reflect newly weighted crosstab freq
		for rimVariable in rimVariables:
			rimVariable.currentFrequencies =\
			aggregateCrosstabFrequencies(rimVariable.structureIndex)

	#Calculates total difference per case at end of iteration
	for rimVariable in rimVariables:
		totalDiffPerCase += \
		diffPerCase(rimVariable.currentFrequencies,\
					rimVariable.desiredFrequencies)
		
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
