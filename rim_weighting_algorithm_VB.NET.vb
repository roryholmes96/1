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
                                    Integrated Security = true", 
                                    server, database))

        'Create a Command object.
        myCmd = myConn.CreateCommand
        myCmd.CommandText = String.Format("SELECT * FROM {0}", table)

        'Open the connection and retrieves data.
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
        'Calculates the index for each possible response in the given set of responses
        'for a survey variable (i.e. enumerates them). e.g. if the possible responses
        'for a variable are 78, 79, 81, 84, this function will return a dictionary in the
        'format ([78, 0], [79, 1], [81, 2], [84, 3]).
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
        'e.g. (["QS0=1&QS2=1&", 46], ["QS0=1&QS2=2", 32]).
        'The "&" is used as a delimiter so that the variable response can be identified
        'when aggregating frequencies and applying weights
        Dim combinedResponsesLists As New ArrayList
        For i = 0 To requiredData.Values(0).Count - 1
            Dim combinedResponses = ""

            For Each listOfResponses In requiredData.Values
                combinedResponses += CStr(listOfResponses(i)) & "&"
            Next

            combinedResponsesLists.Add(combinedResponses)
        Next

        Return calcFrequencies(combinedResponsesLists)
    End Function

    Function getVariableResponseFromCrosstab(header, crosstabPair)
        'Gets the value of a response for a given variable from the key
        'in a given key:value pair in the crosstab, by using the variable
        'header and the next "&" as delimiters.
        Dim startIndex = crosstabPair.Key.IndexOf(header)
        Dim endIndex = crosstabPair.Key.IndexOf("&", startIndex)
        Dim substringLen = endIndex - startIndex
        Dim response = crosstabPair.Key.Substring(startIndex, substringLen)

        Return response
    End Function

    Function aggregateCrosstabFrequencies(header, currentCrosstab)
        'Aggregates the frequencies of responses for a given survey variable in
        'a crosstab. Identifies which crosstab frequencies to add up by identifying
        ' which crosstab keys contain a specific response for the given variable
        Dim frequencies As New SortedDictionary(Of String, Double)

        For Each crosstabPair As KeyValuePair(Of String, Double) In currentCrosstab
            Dim response = getVariableResponseFromCrosstab(header, crosstabPair)

            If frequencies.ContainsKey(response) Then
                frequencies(response) += crosstabPair.Value
            Else
                frequencies.Add(response, crosstabPair.Value)
            End If
        Next

        Return frequencies
    End Function

    Function frequenciesDiff(currentFrequencies As SortedDictionary(Of String, Double),
                             DesiredFrequencies As SortedDictionary(Of String, Double))
        'Calculates the difference between current frequencies (i.e. the 
        'frequencies after current iteration of weighting) and desired frequencies 
        'for each possible response in a survey variable's responses.
        Dim totalDiff As Double

        For Each key In currentFrequencies.Keys
            totalDiff += Math.Abs(currentFrequencies.Item(key) - DesiredFrequencies.Item(key))
        Next

        Return totalDiff
    End Function

    Function diffPerCase(currentFrequencies As SortedDictionary(Of String, Double),
                         desiredFrequencies As SortedDictionary(Of String, Double),
                         actualCrosstab As SortedDictionary(Of String, Double))
        'Calculates the total difference between current and desired frequencies 
        'for a given survey variable, divided by the number of respondents 
        '(this is used to check whether to perform another iteration).
        Dim diff = frequenciesDiff(currentFrequencies, desiredFrequencies)
        Dim sampleSize = 0

        For Each value In actualCrosstab.Values
            sampleSize += value
        Next

        Return diff / sampleSize
    End Function

    Function calcWeights(currentFrequencies As SortedDictionary(Of String, Double),
                         desiredFrequencies As SortedDictionary(Of String, Double))
        'Calculates weights as desiredFrequencies/currentFrequencies quotient
        Dim weights As New ArrayList

        For Each pair As KeyValuePair(Of String, Double) In currentFrequencies
            Dim key = pair.Key
            weights.Add(desiredFrequencies.Item(key) / currentFrequencies.Item(key))
        Next

        Return weights
    End Function

    Sub applyweights(header, responseIndexes, currentCrosstab, weights)
        'Applies weights to the (current) frequencies of a given variable in the
        'current crosstab (i.e. the crosstab after current iteration of 
        'weighting). The value of the response for the given variable is retrieved
        'from a given key:value pair in the crosstab. This value is used to get that
        'response's index position from responseIndexes.The response index is then
        'used to identify which values (frequencies) to apply which weights to in
        'the current crosstab. Utilises a copy of the crosstab to avoid modifying 
        'the crosstab whilst iterating over it.
        Dim currentCrosstabCopy As New SortedDictionary(Of String, Double)
        For Each crosstabPair As KeyValuePair(Of String, Double) In currentCrosstab
            Dim response = getVariableResponseFromCrosstab(header, crosstabPair)
            Dim responseIndex = responseIndexes(response)
            Dim crosstabKey = crosstabPair.Key
            Dim crosstabValue = crosstabPair.Value
            crosstabValue *= weights(responseIndex)
            currentCrosstabCopy.Add(crosstabKey, crosstabValue)
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

        'Retrieves all data from Database.
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

        'Loops through all the data, splits it up into responses, and if the header
        'of one of the required variables appears in the row then this response will
        'be added to it's respective list in the requiredData dictionary. Order is
        'preserved so that e.g. the third case's responses for each variable will
        'appear as index = 2 in the list for each variable.
        For Each row In allData
            Dim splitRow = Split(row, Delimiter:="&")

            For Each response In splitRow

                For Each rimVariable In rimVariables
                    Dim headerString As String
                    headerString = rimVariable.Header

                    If response.Contains(headerString) Then
                        requiredData(headerString).Add(response)
                    End If

                Next
            Next
        Next

        'Updates each instance of rimVariable class by adding attributes Responses, ActualFrequencies
        'CurrentFrequencies, and ResponseIndexes.

        'Responses is the set of response data for a given variable (this is the same list
        'as found in the key for the variable in the requiredData dicitionary).

        'ActualFrequencies is the actual frequencies for each possible response for a given variable,
        'as recorded in data collection

        'CurrentFrequencies is the frequencies during the current iteration of the rim-weighting algorithm
        'i.e. after some weights have been applied. This is initially the same as actual frequencies, but
        'is updated as the rim-weighting algorithm is running.

        'ResponseIndexes is a dictionary of possible responses as keys and their index as a value.
        ' i.e. if the set of possible responses for a variable (e.g. region) are 78, 79, 82, 90
        'ResponseIndexes will be (["78", 0], ["79", 1], ["82", 2], ["90", 3])
        'These are utilised in the rim_weighting algorithm for selecting the correct data to apply the weights to.
        For Each rimVariable In rimVariables
            rimVariable.Responses = requiredData(rimVariable.header)
            rimVariable.ActualFrequencies = calcFrequencies(rimVariable.Responses)
            rimVariable.CurrentFrequencies = rimVariable.ActualFrequencies
            rimVariable.ResponseIndexes = calcResponseIndexes(rimVariable.ActualFrequencies)
        Next

        'Assigns actual and an initial current crosstab 
        Dim actualCrosstab As SortedDictionary(Of String, Double) = crosstab(requiredData)
        Dim currentCrosstab As SortedDictionary(Of String, Double) = crosstab(requiredData)

        'Assigns initial total difference between actual and desired freq per case for
        'all survey variables. i.e. the sum of the totalDiffPerCase fo each survey variable.
        Dim totalDiffPerCase = 0.0
        For Each rimVariable In rimVariables
            For Each i In rimVariable.CurrentFrequencies

            Next
            totalDiffPerCase += diffPerCase(rimVariable.CurrentFrequencies,
                                            rimVariable.DesiredFrequencies,
                                            actualCrosstab)
        Next

        'RIM-Weighting Algorithm
        Dim iteration = 0
        While totalDiffPerCase > 0.000000000000001 And iteration < 50
            totalDiffPerCase = 0.0

            'Calculates and applies weights to crosstab frequencies
            For Each rimVariable In rimVariables
                Dim weights = calcWeights(rimVariable.CurrentFrequencies,
                                          rimVariable.DesiredFrequencies)

                applyweights(rimVariable.header,
                             rimVariable.ResponseIndexes,
                             currentCrosstab,
                             weights)

                'Updates current frequencies to refelct newly weighted crosstab frequencies
                For Each _rimVariable In rimVariables
                    _rimVariable.currentFrequencies =
                        aggregateCrosstabFrequencies(_rimVariable.header, currentCrosstab)
                Next
            Next

            'Calculates total difference per case at end of iteration
            For Each rimVariable In rimVariables
                totalDiffPerCase += diffPerCase(rimVariable.CurrentFrequencies,
                                                rimVariable.DesiredFrequencies,
                                                actualCrosstab)
            Next

            'Increases iteration and prints current iteration and diff per case
            iteration += 1

            Console.WriteLine(String.Format("{0}iteration: {1}", vbCrLf, iteration))
            Console.WriteLine(String.Format("total diff per case: {0}", totalDiffPerCase))

        End While

        'Calculates final weights based on differene between actual and current crosstab frequencies
        Dim finalWeights = calcWeights(actualCrosstab, currentCrosstab)

        'Writes keys with weights to console
        Console.WriteLine(String.Format("{0}Results in the format:", vbCrLf))

        For i = 0 To rimVariables.count - 1
            Console.Write(String.Format("{0}response&", rimVariables(i).header))
        Next

        Console.WriteLine(String.Format(": weight{0}", vbCrLf))

        For i = 0 To finalWeights.count - 1
            Dim keysWithWeights = String.Format("{0}: {1}", actualCrosstab.Keys(i), finalWeights(i))
            Console.WriteLine(keysWithWeights)
        Next

        Console.ReadLine()
    End Sub

    Sub Main()
        'List containing all instances of the RimVariable object
        Dim rimVariables As New List(Of Object)

        'Enter database info here
        Dim server = ".\sqlexpress"
        Dim database = "Pokerstars"
        Dim table = "pokerstars"
        Dim column = 0

        'Enter header and desired frequency info here
        Dim header1 = "QS2="
        Dim desiredFrequencies1 As New SortedDictionary(Of String, Double) From {{"QS2=1", 300}, {"QS2=2", 232}}
        rimVariables.Add(New RimVariable(header1, desiredFrequencies1))

        Dim header2 = "QS3="
        Dim desiredFrequencies2 As New SortedDictionary(Of String, Double) From {{"QS3=1", 53}, {"QS3=2", 88}, {"QS3=3", 126}, {"QS3=4", 95}, {"QS3=5", 170}}
        rimVariables.Add(New RimVariable(header2, desiredFrequencies2))

        Dim header3 = "QS4="
        Dim desiredFrequencies3 As New SortedDictionary(Of String, Double) From {{"QS4=79", 26}, {"QS4=80", 65}, {"QS4=81", 55}, {"QS4=82", 45}, {"QS4=83", 29}, {"QS4=84", 30}, {"QS4=85", 40}, {"QS4=86", 87}, {"QS4=87", 66}, {"QS4=88", 58}, {"QS4=89", 15}, {"QS4=90", 16}}
        rimVariables.Add(New RimVariable(header3, desiredFrequencies3))

        CalculateRimWeights(server, database, table, column, rimVariables)
    End Sub

End Module
