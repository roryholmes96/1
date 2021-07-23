Imports System.Data.SqlClient

Module RimWeightingAlgorithm
    Private myConn As SqlConnection
    Private myCmd As SqlCommand
    Private myReader As SqlDataReader
    Private results As String
    Function RetrieveData(server, database, table, column)
        'Create a Connection object.
        myConn = New SqlConnection(String.Format("Server = {0}; 
                                    Database = {1}; 
                                    Integrated Security = true", server, database))

        'Create a Command object.
        myCmd = myConn.CreateCommand
        myCmd.CommandText = String.Format("SELECT * FROM {0}", table)

        'Open the connection and retieves data.
        myConn.Open()
        myReader = myCmd.ExecuteReader()

        'Adds each row from specified column to a list titled 'data'
        Dim data As New ArrayList
        For Each row In myReader
            data.Add(row(column))
        Next

        'Closes connection to database
        myConn.Close()

        Return data
    End Function

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
        'for a variable are 78, 79, 81, 84, this function will return a dictionary in the
        'format ([78, 0], [79, 1], [81, 2], [84, 3])
        Dim curIndex = 0
        Dim responseIndexes As New SortedDictionary(Of String, Integer)

        For Each key In frequencies.Keys
            responseIndexes.Add(key, curIndex)
            curIndex += 1
        Next

        Return responseIndexes
    End Function

    Function crosstab(requiredData As Dictionary(Of String, ArrayList))
        'Crosstabs the lists of responses for each item in the requiredData dict.
        'The crosstab is a dictionary in which there is a key for each possible 
        'combination of responses, with the frequency of respondents who responded
        'in that combination as the value.
        Dim combinedResponsesLists As New ArrayList
        For i = 0 To requiredData.Values(0).Count - 1
            Dim combinedResponses = ""

            For Each listOfResponses In requiredData.Values
                combinedResponses += CStr(listOfResponses(i))
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
        'Calculates the difference between current frequencies (i.e. the 
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
        Public Property Header As String
        Public Property DesiredFrequencies As SortedDictionary(Of String, Double)
        Public Property Responses As ArrayList
        Public Property Indx As Integer
        Public Property ActualFrequencies As SortedDictionary(Of String, Double)
        Public Property CurrentFrequencies As SortedDictionary(Of String, Double)
        Public Property ResponseIndexes As SortedDictionary(Of String, Integer)

        Public Sub New(ByVal _header As String,
                       ByVal _desiredFrequencies As SortedDictionary(Of String, Double))

            Me.Header = _header
            Me.DesiredFrequencies = _desiredFrequencies

        End Sub

    End Class

    Sub CalculateRimWeights(server, database, table, column, rimVariables)

        'Retrieves all Data from Database.
        Dim allData = RetrieveData(server, database, table, column)

        'Creates a dictionary for the required data in the form
        ' (["QsX", listOfResponses], ["QsY", listOfResponses]).
        Dim requiredData As New Dictionary(Of String, ArrayList)
        For Each rimVariable In rimVariables
            Dim headerString As String
            headerString = rimVariable.Header

            Dim emptyList As New ArrayList

            requiredData.Add(headerString, emptyList)
        Next

        'Loops through all the data, splits it up into responses, and if the header of one of the required variables appears
        'in the row then this response will be added to it's respective list in the requiredData dictionary.
        'Order is preserved so that e.g. the third case's responses for each variable will be appear as index = 2 in the list
        'for each variable.
        For Each row In allData
            Dim splitRow = Split(row, Delimiter:="&")

            For Each response In splitRow

                For Each rimVariable In rimVariables
                    Dim headerString As String
                    headerString = rimVariable.Header

                    If response.Contains(headerString) Then
                        requiredData(headerString).Add(response.Replace(String.Format("{0}=", headerString), ""))

                    End If

                Next

            Next
        Next

        'Assigns actual And an initial current crosstab 
        Dim actualCrosstab As SortedDictionary(Of String, Double) = crosstab(requiredData)
        Dim currentCrosstab As SortedDictionary(Of String, Double) = crosstab(requiredData)

        'Updates each instance of rimVariable class by adding attributes Indx, Responses, ActualFrequencies
        'CurrentFrequencies, and ResponseIndexes.

        'Indx is the index of the variable in rimVariables, requiredData and the crosstabs.

        'Responses is the set of response data for a given variable (this is the same list
        'as found in the key for the variable in the requiredData dicitionary.

        'ActualFrequencies is the actual frequencies for each possible response for a given variable,
        'as recorded in data collection

        'CurrentFrequencies is the frequencies during the current iteration of the rim-weighting algorithm
        'i.e. after some weights have been applied. This is initially the same as actual frequencies, but
        'is updated as the rim-weighting algorithm is running

        'ResponseIndexes is a dictionary of possible responses as keys and their index as a value.
        ' i.e. if the set of possible responses for a variable (e.g. region) are 78, 79, 82, 90
        'ResponseIndexes will be (["78", 0], ["79", 1], ["82", 2], ["90", 3])
        'These are utilised in the rim_weighting algorithm for selecting the correct data to apply the weights to
        For Each rimVariable In rimVariables
            rimVariable.Indx = rimVariables.IndexOf(rimVariable)
            rimVariable.Responses = requiredData(rimVariable.header)
            rimVariable.ActualFrequencies = calcFrequencies(rimVariable.Responses)
            rimVariable.CurrentFrequencies = rimVariable.ActualFrequencies
            rimVariable.ResponseIndexes = calcResponseIndexes(rimVariable.ActualFrequencies)
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
                applyweights(rimVariable.Indx, rimVariable.ResponseIndexes, currentCrosstab, weights)

                'Updates current frequencies to refelct newly weighted crosstab frequencies
                For Each _rimVariable In rimVariables
                    _rimVariable.currentFrequencies = aggregateCrosstabFrequencies(_rimVariable.Indx, currentCrosstab)
                Next
            Next

            'Calculates total difference per case at end of iteration
            For Each rimVariable In rimVariables
                totalDiffPerCase += diffPerCase(rimVariable.CurrentFrequencies, rimVariable.DesiredFrequencies, actualCrosstab)
            Next

            'increases iteration and prints current iteration and diff per case
            iteration += 1

            Console.WriteLine(String.Format("{0}iteration: {1}", vbCrLf, iteration))
            Console.WriteLine(String.Format("total diff per case: {0}", totalDiffPerCase))

        End While

        'Calculates final weights based on differene between actual and current crosstab frequencies
        Dim finalWeights = calcWeights(actualCrosstab, currentCrosstab)

        'Writes keys with weights to console
        Console.WriteLine(String.Format("{0}Results in the format:", vbCrLf))

        For i = 0 To rimVariables.count - 1
            Console.Write(String.Format(" {0} response", rimVariables(i).header))
        Next

        Console.WriteLine(String.Format(": weight{0}", vbCrLf))

        For i = 0 To finalWeights.count - 1
            Dim keysWithWeights = String.Format("{0}: {1}", actualCrosstab.Keys(i), finalWeights(i))
            Console.WriteLine(keysWithWeights)
        Next

        Console.ReadLine()
    End Sub

    Sub Main()

        Dim server = ".\sqlexpress"
        Dim database = "Nivea"
        Dim table = "weighted_custom"
        Dim column = 6

        Dim rimVariables As New List(Of Object)

        Dim header1 = "Qs0"
        Dim desiredFrequencies1 As New SortedDictionary(Of String, Double) From {{"1", 700}, {"2", 805}}
        rimVariables.Add(New RimVariable(header1, desiredFrequencies1))

        Dim header2 = "Qs3"
        Dim desiredFrequencies2 As New SortedDictionary(Of String, Double) From {{"1", 502}, {"2", 555}, {"3", 400}, {"4", 48}}
        rimVariables.Add(New RimVariable(header2, desiredFrequencies2))

        CalculateRimWeights(server, database, table, column, rimVariables)
    End Sub

End Module
