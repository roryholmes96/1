filename = \
r'C:\Users\44797\Downloads\4943-21 Nivea Adcepts Brazil0_21060704.csv'

#Creates lists for each column
serial_list = []
gender_list = []
age_list = []
deoderant_use_list = []

#Splits data in csv rows by ',' and appends each column to respective list
with open(filename) as f:
    for row in f:
        serial_list.append(row.split(',')[0])
        gender_list.append(row.split(',')[1])
        age_list.append(row.split(',')[2])
        deoderant_use_list.append(row.split(',')[3])

#Removes '\n' from deoderant list
deoderant_use_list = [i.rstrip() for i in deoderant_use_list]

#Removes column headers from lists
serial_list.remove('ï»¿HWSerial')
gender_list.remove('Qs0')
age_list.remove('Qs1_1')
deoderant_use_list.remove('Qs3')

#Converts list items from strings to ints
for string in range(0, len(deoderant_use_list)):
    deoderant_use_list[string] = int(deoderant_use_list[string])

for string in range(0, len(gender_list)):
    gender_list[string] = int(gender_list[string])

for string in range(0, len(age_list)):
    age_list[string] = int(age_list[string])

#Defines functions to perform various statistical analyses
def get_frequencies(variable_list):
    '''Calculates frequencies for variable'''
    variable_frequencies = {}
    for variable in variable_list:
        if variable in variable_frequencies.keys():
            variable_frequencies[variable] +=1
        else:
            variable_frequencies[variable] = 1
    for k, v in sorted(variable_frequencies.items()):
        print(f'{k}: {v}')

def mean(variable_list):
    '''Calculates mean of a variable'''
    mean = sum(variable_list)/len(variable_list)
    return mean

def standard_deviation(variable_list):
    '''Calculates standard deviation of a variable'''
    deviations =\
    [(variable - mean(variable_list)) ** 2 for variable in variable_list]
    variance = (sum(deviations)/(len(deviations)))
    standard_deviation = variance** (1/2)
    return(standard_deviation)

def get_descriptives(variable_list):
    '''Gets descriptive statistics for variable'''
    print(f'min: {min(variable_list)}')
    print(f'max: {max(variable_list)}')
    print(f'mean: {mean(variable_list)}')
    print(f'standard deviation: {standard_deviation(variable_list)}')

def cross_tabulate_frequencies(variable_list1, variable_list2):
    '''Cross-tabulates 2 variables and returns frequencies'''
    cross_tabulation_variables = list(zip(variable_list1, variable_list2))
    cross_tabulation_frequencies = {}
    for t in cross_tabulation_variables:
        if t in cross_tabulation_frequencies.keys():
            cross_tabulation_frequencies[t] +=1
        else:
            cross_tabulation_frequencies[t] =1
    return(cross_tabulation_frequencies)

def cross_tabulate_means(variable_list1, variable_list2, variable_list3):
    '''Cross-tabulates 2 variables and returns means of 3rd variable'''
    cross_tabulation_frequencies = \
    cross_tabulate_frequencies(variable_list1, variable_list2)
    
    cross_tabulation_variables = \
    list(zip(variable_list1, variable_list2, variable_list3))
    cross_tabulation_sums = {}
    
    for x, y, z in cross_tabulation_variables:
        if (x,y) in cross_tabulation_sums.keys():
            cross_tabulation_sums[(x,y)] += z
        else:
            cross_tabulation_sums[(x,y)] = z

    frequency_sum_list = list\
    (zip(cross_tabulation_sums.values(),cross_tabulation_frequencies.values()))

    cross_tabulation_means = []
    for x,y in frequency_sum_list:
        cross_tabulation_means.append(x/y)

    return cross_tabulation_means

def print_cross_tabulation(variable_list1, variable_list2, variable_list3):
    '''Formats and prints cross-tabulation results'''
    cross_tabulation_frequencies = \
    cross_tabulate_frequencies(variable_list1, variable_list2)

    cross_tabulation_means = \
    cross_tabulate_means (variable_list1, variable_list2, variable_list3)

    full_cross_tabulation = list(zip(cross_tabulation_frequencies.keys(),\
    cross_tabulation_frequencies.values(),\
    cross_tabulation_means))

    for x,y,z in sorted(full_cross_tabulation): 
        print(f'{x}: frequency = {y}, mean age = {z}')

age_bin_list = []
for i in range(len(age_list)):
    if age_list[i] < 11:
        age_bin_list.append('age_0_10')
    elif age_list[i] < 21:
        age_bin_list.append('age_11_20')
    elif age_list[i] < 31:
        age_bin_list.append('age_21_30')    
    elif age_list[i] < 41:
        age_bin_list.append('age_31_40')
    elif age_list[i] < 51:
        age_bin_list.append('age_41_50')
    elif age_list[i] < 61:
        age_bin_list.append('age_51_60')
    elif age_list[i] < 71:
        age_bin_list.append('age_61_70')
    elif age_list[i] < 81:
        age_bin_list.append('age_71_80')

#Performs analyses on data and prints results
print('Gender Frequencies:')
get_frequencies(gender_list)

print('\nDeoderant Use Frequencies:')
get_frequencies(deoderant_use_list)

print('\nAge Descriptives:')
get_descriptives(age_list)

print('\nAge Bin Frequencies:')
get_frequencies(age_bin_list) 

print('\nCross-Tabulation with Frequencies and Mean Age'\
' (Gender, Deoderant Use):')
print_cross_tabulation(gender_list, deoderant_use_list, age_list)
