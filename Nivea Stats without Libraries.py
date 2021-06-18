file = open(r'C:\Users\44797\Downloads\4943-21 Nivea Adcepts Brazil0_21060704.csv')

#Creates lists for each column
ageList=[]
genderList=[]
deoderantList=[]

#Splits data in csv rows by ',' and appends each column to respective list
for row in file:
    ageList.append(row.split(',')[2])
    genderList.append(row.split(',')[1])
    deoderantList.append(row.split(',')[3])

#Removes '\n' from deoderant list
deoderantList = [i.strip('\n') for i in deoderantList]

#Removes column headers from lists
deoderantList.remove('Qs3')
genderList.remove('Qs0')
ageList.remove('Qs1_1')

#Converts list items from strings to ints
for string in range(0, len(deoderantList)):
    deoderantList[string] = int(deoderantList[string])

for string in range(0, len(genderList)):
    genderList[string] = int(genderList[string])

for string in range(0, len(ageList)):
    ageList[string] = int(ageList[string])
    
#Calculates frequencies for Gender and Deoderant Use
genderFrequency = {}
for gender in genderList:
    if gender in genderFrequency.keys():
        genderFrequency[gender] += 1
    else:
        genderFrequency[gender] = 1

deoderantFrequency = {}
for deoderant in deoderantList:
    if deoderant in deoderantFrequency.keys():
        deoderantFrequency[deoderant] += 1
    else:
        deoderantFrequency[deoderant] = 1

print('Deoderant Use Frequencies')
print(deoderantFrequency)
print('')
print('Gender Frequencies')
print(genderFrequency)
print('')

#Calculates descritptive statistics for Age
minAge = min(ageList)
maxAge = max(ageList)
meanAge = (sum(ageList)/len(ageList))
deviationsAge = [(x - meanAge) ** 2 for x in ageList]
varianceAge = (sum(deviationsAge)/(len(deviationsAge)))
sdAge = varianceAge ** (1/2)

print('Age Descriptive Statistics')
print('Min Age: ' + str(minAge))
print('Max Age: ' + str(maxAge))
print('Mean Age: ' + str(meanAge))
print('Standard Deviation: ' + str(sdAge))
print('')


#Cross-Tabulation (creates touples for each gn, dn and calculates
#frequencies of tuples i.e. cross-tabulation
gxd = list(zip(genderList, deoderantList)) 
gxdFrequency = {}
for touple in gxd:
    if touple in gxdFrequency.keys():
        gxdFrequency[touple] += 1
    else:
        gxdFrequency[touple] = 1

print('Cross-Tabulation Frequencies for Gender, Deoderant Use')
print(gxdFrequency)
print('')

#Cross-Tabulation with mean age (creates a 3-tuple for each gn, dn and an
#and then creates lists of an for each gn, dn then calculates mean of these
#age lists
gxdxa = list(zip(genderList, deoderantList, ageList))
g1xd1Age = [z for x, y, z in gxdxa if x == 1 and y == 1]
g1xd2Age = [z for x, y, z in gxdxa if x == 1 and y == 2]
g1xd3Age = [z for x, y, z in gxdxa if x == 1 and y == 3]
g1xd4Age = [z for x, y, z in gxdxa if x == 1 and y == 4]
g2xd1Age = [z for x, y, z in gxdxa if x == 2 and y == 1]
g2xd2Age = [z for x, y, z in gxdxa if x == 2 and y == 2]
g2xd3Age = [z for x, y, z in gxdxa if x == 2 and y == 3]
g2xd4Age = [z for x, y, z in gxdxa if x == 2 and y == 4]
g3xd1Age = [z for x, y, z in gxdxa if x == 3 and y == 1]
g3xd2Age = [z for x, y, z in gxdxa if x == 3 and y == 2]
g3xd3Age = [z for x, y, z in gxdxa if x == 3 and y == 3]
g3xd4Age = [z for x, y, z in gxdxa if x == 3 and y == 4]
g4xd1Age = [z for x, y, z in gxdxa if x == 4 and y == 1]
g4xd2Age = [z for x, y, z in gxdxa if x == 4 and y == 2]
g4xd3Age = [z for x, y, z in gxdxa if x == 4 and y == 3]
g4xd4Age = [z for x, y, z in gxdxa if x == 4 and y == 4]

g1xd1AgeMean = (sum(g1xd1Age)/len(g1xd1Age))
g1xd2AgeMean = (sum(g1xd2Age)/len(g1xd2Age))
g1xd3AgeMean = (sum(g1xd3Age)/len(g1xd3Age))
g1xd4AgeMean = (sum(g1xd4Age)/len(g1xd4Age))
g2xd1AgeMean = (sum(g2xd1Age)/len(g2xd1Age))
g2xd2AgeMean = (sum(g2xd2Age)/len(g2xd2Age))
g2xd3AgeMean = (sum(g2xd3Age)/len(g2xd3Age))
g2xd4AgeMean = (sum(g2xd4Age)/len(g2xd4Age))
##g3xd1AgeMean = (sum(g3xd1Age)/len(g3xd1Age))
g3xd2AgeMean = (sum(g3xd2Age)/len(g3xd2Age))
g3xd3AgeMean = (sum(g3xd3Age)/len(g3xd3Age))
##g3xd4AgeMean = (sum(g3xd4Age)/len(g3xd4Age))
g4xd1AgeMean = (sum(g4xd1Age)/len(g4xd1Age))
##g4xd2AgeMean = (sum(g4xd2Age)/len(g4xd2Age))
##g4xd3AgeMean = (sum(g4xd3Age)/len(g4xd3Age))
##g4xd4AgeMean = (sum(g4xd4Age)/len(g4xd4Age))

print('Cross-Tabulation Mean Ages for Gender, Deoderant Use')
print('(1,1): ' + str(g1xd1AgeMean))
print('(1,2): ' + str(g1xd2AgeMean))
print('(1,3): ' + str(g1xd3AgeMean))
print('(1,4): ' + str(g1xd4AgeMean))
print('(2,1): ' + str(g2xd1AgeMean))
print('(2,2): ' + str(g2xd2AgeMean))
print('(2,3): ' + str(g2xd3AgeMean))
print('(2,4): ' + str(g2xd4AgeMean))
##print('(3,1): ' + str(g3xd1AgeMean))
print('(3,2): ' + str(g3xd2AgeMean))
print('(3,3): ' + str(g3xd3AgeMean))
##print('(3,4): ' + str(g3xd4AgeMean))
print('(4,1): ' + str(g4xd1AgeMean))
##print('(4,2): ' + str(g4xd2AgeMean))
##print('(4,3): ' + str(g4xd3AgeMean))
##print('(4,4): ' + str(g4xd4AgeMean))
