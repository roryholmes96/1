Imports System.Data.SqlClient

Module RimWeightingAlgorithm
    Private myConn As SqlConnection
    Private myCmd As SqlCommand
    Private myReader As SqlDataReader
    Private results As String

    Function calcFrequencies(responses As ArrayList)
        'Calculates the frequencies for each possible response in a survey 
        'variable's list of responses.
        Dim frequencies As New SortedDictionary(Of String, Double)

        For Each response In responses
            If frequencies.ContainsKey(response) Then
                frequencies(response) += 1
            Else
                frequencies.Add(response, 1)
            End If
        Next

        Return frequencies
    End Function
    Function calcResponseIndexes(frequencies As SortedDictionary(Of String, Double))
        'calcs the index for each possible response in the given set of responses for
        'a response variable (i.e. enumerates them). e.g. if the possible responses
        'for region are 78, 79, 81, 84, this function will return a dictionary in the
        'format ([78, 0], [79, 1], [81, 2], [84, 3])
        Dim curIndex = 0
        Dim responseIndexes As New SortedDictionary(Of String, Integer)

        For Each key In frequencies.Keys
            responseIndexes.Add(key, curIndex)
            curIndex += 1
        Next

        Return responseIndexes
    End Function

    Function crosstab(ParamArray responsesLists())
        'Crosstabs the lists of responses for multiple survey variables. The
        'crosstab is a dictionary in which there is a key for each possible 
        'combination of responses, with the frequency of respondents who responded
        'in that combination as the value
        Dim combinedResponsesLists As New ArrayList
        For i = 0 To responsesLists(0).count - 1
            Dim combinedResponses = ""

            For Each lst In responsesLists
                combinedResponses += CStr(lst(i))
            Next

            combinedResponsesLists.Add(combinedResponses)
        Next

        Return calcFrequencies(combinedResponsesLists)
    End Function


    Function aggregateCrosstabFrequencies(crosstabIndex, currentCrosstab)
        'Aggregates the frequencies of responses for each survey variable in
        'a crosstab
        Dim frequencies As New SortedDictionary(Of String, Double)

        For Each pair As KeyValuePair(Of String, Double) In currentCrosstab
            Dim key = pair.Key
            Dim frequency = pair.Value

            If frequencies.ContainsKey(key(crosstabIndex)) Then
                frequencies(key(crosstabIndex)) += frequency
            Else
                frequencies.Add(key(crosstabIndex), frequency)
            End If
        Next

        Return frequencies
    End Function

    Function frequenciesDiff(currentFrequencies As SortedDictionary(Of String, Double), DesiredFrequencies As SortedDictionary(Of String, Double))
        'alculates the difference between current frequencies (i.e. the 
        'frequencies after current iteration of weighting) And desired frequencies 
        'for aach possible response in a survey variable's responses.
        Dim totalDiff As Double

        For Each key In currentFrequencies.Keys
            totalDiff += Math.Abs(currentFrequencies.Item(key) - DesiredFrequencies.Item(key))
        Next

        Return totalDiff
    End Function

    Function diffPerCase(currentFrequencies As SortedDictionary(Of String, Double), desiredFrequencies As SortedDictionary(Of String, Double), actualCrosstab As SortedDictionary(Of String, Double))
        'Calculates the total difference between current And desired frequencies 
        'for a given survey variable, divided by the number of respondents 
        '(this is used to check whether to perform another iteration).
        Dim diff = frequenciesDiff(currentFrequencies, desiredFrequencies)
        Dim sampleSize = 0

        For Each value In actualCrosstab.Values
            sampleSize += value
        Next

        Return diff / sampleSize
    End Function

    Function calcWeights(currentFrequencies As SortedDictionary(Of String, Double), desiredFrequencies As SortedDictionary(Of String, Double))
        'Calculates weights as desiredFrequencies/currentFrequencies quotient
        Dim weights As New ArrayList

        For Each pair As KeyValuePair(Of String, Double) In currentFrequencies
            Dim key = pair.Key
            weights.Add(desiredFrequencies.Item(key) / currentFrequencies.Item(key))
        Next

        Return weights
    End Function

    Sub applyweights(crosstabIndex, responseIndexes, currentCrosstab, weights)
        'Applies weights to the (current) frequencies of a given variable in the
        'current crosstab (i.e. the crosstab after current iteration of 
        'weighting). The crosstabIndex passed as an argument denotes the 
        'position of the survey variable in the current crosstab's key. For 
        'each item in the crosstab, this formula retrieves the value of the 
        'response (e.g. 78 for region 78, or 2 for gender 2). It then uses this 
        'value to get that response's index position in the ordered set of 
        'possible responses i.e. (0 if 78 is the lowest value in the set of region 
        'responses). This index position is retrieved from the responseIndexes
        'passed as an argument. The response index is then used to identify which
        'values (frequencies) to apply which weights to in the current crosstab.
        Dim currentCrosstabCopy As New SortedDictionary(Of String, Double)
        For Each pair As KeyValuePair(Of String, Double) In currentCrosstab
            Dim key = pair.Key
            Dim value = pair.Value
            Dim response = key(crosstabIndex)
            Dim responseIndex = responseIndexes(response)
            value *= weights(responseIndex)
            currentCrosstabCopy.Add(key, value)
        Next

        For Each pair As KeyValuePair(Of String, Double) In currentCrosstabCopy
            Dim key = pair.Key
            Dim value = pair.Value
            currentCrosstab.Item(key) = value
        Next

    End Sub

    Public Class RimVariable
        'Represents survey variables to be used in RIM Weighting

        Public Property Responses As ArrayList
        Public Property ActualFrequencies As SortedDictionary(Of String, Double)
        Public Property CurrentFrequencies As SortedDictionary(Of String, Double)
        Public Property DesiredFrequencies As SortedDictionary(Of String, Double)
        Public Property CrosstabIndex As Double
        Public Property ResponseIndexes As SortedDictionary(Of String, Integer)

        Public Sub New(ByVal _responses As ArrayList,
                   ByVal _desiredFrequencies As SortedDictionary(Of String, Double),
                   ByVal _crosstabIndex As Double)

            Me.Responses = _responses
            Me.ActualFrequencies = calcFrequencies(Me.Responses)
            Me.CurrentFrequencies = Me.ActualFrequencies
            Me.DesiredFrequencies = _desiredFrequencies
            Me.CrosstabIndex = _crosstabIndex
            Me.ResponseIndexes = calcResponseIndexes(Me.ActualFrequencies)

        End Sub

    End Class

    Sub Main()
        'Create a Connection object.
        myConn = New SqlConnection("Server = .\sqlexpress; Database = Nivea; Integrated Security = true")

        'Create a Command object.
        myCmd = myConn.CreateCommand
        myCmd.CommandText = "SELECT * FROM Nivea.dbo.weighted_custom"

        'Open the connection and retieves data.
        myConn.Open()
        myReader = myCmd.ExecuteReader()

        'Adds each row (in column 6 for this example) to a list titled 'data'
        Dim data As New ArrayList
        For Each row In myReader
            data.Add(row(6))
        Next

        'Closes connection to database
        myConn.Close()

        'Creates list for set of responses for each survey variable
        Dim genderResponses As New ArrayList
        Dim ageResponses As New ArrayList
        Dim ageResponsesBins As New ArrayList

        'Iterates through rows, adding each survey variable response to respective list
        For Each row In data
            Dim splitRow = Split(row, Delimiter:="&")

            For Each response In splitRow
                If response.Contains("Qs0") Then
                    genderResponses.Add(response.Replace("Qs0=", ""))
                ElseIf response.Contains("Qs1_1") Then
                    ageResponses.Add(response.Replace("Qs1_1=", ""))
                End If
            Next
        Next

        'Splits age data into bins
        For Each response In ageResponses
            ageResponsesBins.Add(Math.Floor((response - 1) / 10))
        Next

        'Arbitrary desired Frequency distributions
        Dim desiredAgeFrequencies As New SortedDictionary(Of String, Double) From {
        {"1", 75}, {"2", 400}, {"3", 500}, {"4", 300}, {"5", 200}, {"6", 29}, {"7", 1}}

        Dim desiredGenderFrequencies As New SortedDictionary(Of String, Double) From {
        {"1", 700}, {"2", 805}}

        'Creates list which contains lists of responses for each survey vairable to
        'be used in rim-weighting
        Dim surveyVariableResponses As New ArrayList({ageResponsesBins, genderResponses})

        'Creates list which contains the frequency distribution dictonaries for each 
        'survey variable To be used in rim-weighting
        Dim desiredFrequencies As New ArrayList({desiredAgeFrequencies, desiredGenderFrequencies})

        'Assigns actual And an initial current crosstab 
        Dim actualCrosstab As New SortedDictionary(Of String, Double)
        actualCrosstab = crosstab(ageResponsesBins, genderResponses)

        Dim currentCrosstab As New SortedDictionary(Of String, Double)
        currentCrosstab = crosstab(ageResponsesBins, genderResponses)

        'Creates crosstabIndexes list which contains the lists of crosstabIndexes for 
        'each item nn surveyVariableResponses list. crosstabIndexes are the position Of 
        'a variable's corresponding response in the crosstab key . e.g. if the
        'crosstab is in the format ("genderResponse ageResponse",frequency), the 
        'crosstab index  is 0 For genderResponses and 1 For ageResponses 
        Dim crosstabIndexes As New List(Of Double)

        Dim curIndex = 0
        For Each item In surveyVariableResponses
            crosstabIndexes.Add(curIndex)
            curIndex += 1
        Next

        'assigns each variable with respective data to RimVariable class and adds each
        'instance of this class to rimVariables list
        Dim rimVariables As New ArrayList
        For i = 0 To crosstabIndexes.Count - 1
            Dim rimVariable As New RimVariable(surveyVariableResponses(i), desiredFrequencies(i), crosstabIndexes(i))
            rimVariables.Add(rimVariable)
        Next

        'assigns initial total difference between actual and desired freq per case for
        'all survey variables. i.e. the sum of the totalDiffPerCase fo each survey variable
        Dim totalDiffPerCase = 0.0
        For Each rimVariable In rimVariables
            For Each i In rimVariable.CurrentFrequencies

            Next
            totalDiffPerCase += diffPerCase(rimVariable.CurrentFrequencies, rimVariable.DesiredFrequencies, actualCrosstab)
        Next

        'RIM-Weighting Algorithm
        Dim iteration = 0
        While totalDiffPerCase > 0.0000000000000001 And iteration < 50
            totalDiffPerCase = 0.0

            'Calculates and applies weights to crosstab frequencies
            For Each rimVariable In rimVariables
                Dim weights = calcWeights(rimVariable.CurrentFrequencies, rimVariable.desiredFrequencies)
                applyweights(rimVariable.CrosstabIndex, rimVariable.ResponseIndexes, currentCrosstab, weights)

                'Updates current frequencies to refelct newly weighted crosstab frequencies
                For Each _rimVariable In rimVariables
                    _rimVariable.currentFrequencies = aggregateCrosstabFrequencies(_rimVariable.CrosstabIndex, currentCrosstab)
                Next
            Next

            'Calculates total difference per case at end of iteration
            For Each rimVariable In rimVariables
                totalDiffPerCase += diffPerCase(rimVariable.CurrentFrequencies, rimVariable.DesiredFrequencies, actualCrosstab)
            Next

            'increases iteration and prints current iteration and diff per case
            iteration += 1
            Dim string1 = String.Format("iteration: {0}", iteration)
            Dim string2 = String.Format("total diff per case: {0}", totalDiffPerCase)
            Console.WriteLine(string1)
            Console.WriteLine(string2)

        End While

        'Calculates final weights based on differene between actual and current crosstab frequencies
        Dim finalWeights = calcWeights(actualCrosstab, currentCrosstab)

        'Writes keys with weights to console
        For i = 0 To finalWeights.count - 1
            Dim keysWithWeights = String.Format("{0}: {1}", actualCrosstab.Keys(i), finalWeights(i))
            Console.WriteLine(keysWithWeights)
        Next

        Console.ReadLine()
    End Sub

End Module
