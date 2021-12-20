Public Sub DRAW()

    Dim def_xl As Long, def_yu As Long, def_xr As Long, def_yl As Long
    'defect map upper,lower,left,right define
    Dim bin_xl As Long, bin_yu As Long, bin_xr As Long, bin_yl As Long
    'defect map upper,lower,left,right define
    'Dim diecount_bin As Long, diecount_def As Long
    'Dim dfx_shift As Integer, dfy_shift As Integer  'map shift count
    Dim index_binx As Long, index_biny As Long, index_defx As Long, index_defy As Long
    
    Dim col
    Dim rowx
    Dim cellx
    Dim dfrow_end, binrow_end
    '以下获取defect map和bin map的左行值，右行值和上列值，下列值；
        Worksheets("defect").Activate
        dfrow_end = Range("a277").End(xlDown).Row - 1
        With Worksheets("defect")
            def_xl = WorksheetFunction.Min(Range("b277:b" & dfrow_end))
            def_xr = WorksheetFunction.Max(Range("b277:b" & dfrow_end))
            def_yu = WorksheetFunction.Min(Range("c277:c" & dfrow_end))
            def_yl = WorksheetFunction.Max(Range("c277:c" & dfrow_end))
        End With
    
        Worksheets("bin").Activate
        binrow_end = Range("d2").End(xlDown).Row
        With Worksheets("bin")
            bin_xl = WorksheetFunction.Min(Range("d3:d" & binrow_end))
            bin_xr = WorksheetFunction.Max(Range("d3:d" & binrow_end))
            bin_yu = WorksheetFunction.Min(Range("e3:e" & binrow_end))
            bin_yl = WorksheetFunction.Max(Range("e3:e" & binrow_end))
        End With
        '以上获取defect map和bin map的左行值，右行值和上列值，下列值；
    
        '以下定义die的大小
        Worksheets("com map").Activate
        Worksheets("com map").Range("a:iv").Clear
              
        '以下定义BIN MAP
        For Each cellx In Worksheets("bin").Range("d3:d" & binrow_end)
            index_binx = -cellx.Offset(0, 1).Value  'Abs(bin_yu)
            If bin_xl <= 0 Then
            index_biny = Abs(bin_xl) + cellx.Value
            Else
            index_biny = cellx.Value
            End If
            Worksheets("com map").cells(index_binx + 10, index_biny + 10).Interior.ColorIndex = 4
            Worksheets("com map").cells(index_binx + 10, index_biny + 10).Borders.ColorIndex = 1
        Next
            
        '以下定义DEFECT MAP
        For Each cellx In Worksheets("defect").Range("b277:b" & dfrow_end)
            index_defx = def_yl + 1 - cellx.Offset(0, 1).Value
            index_defy = Abs(def_xl) + 1 + cellx.Value
            Worksheets("com map").cells(index_defx + 10, index_defy + 10).Value = "D"
        Next

        
        Worksheets("com map").Range("a2:iv300").RowHeight = 385 / (bin_yl - bin_yu)     '定义DIE高度
        Worksheets("com map").Columns("a:ia").ColumnWidth = (40 / (bin_xr - bin_xl))   '定义DIE宽度
        Worksheets("com map").Range("a2:iv300").Font.Size = 6   '定义字母“D”大小
        
        
        If (def_xr - def_xl) = (bin_xr - bin_xl) And (def_yl - def_yu) = (bin_yl - bin_yu) Then

        Else
            MsgBox "Defect Map的列数或行数和Bin Map不符，请在自动画完后修正"

        End If
        
        Worksheets("com map").Range("a1") = "Bin map:" & Left((Worksheets("bin").Range("a3")), 4) & "-" & Worksheets("bin").Range("b3") _
                                            & "   " & "Defect map:" & Worksheets("defect").Range("b8") & "@" & Worksheets("defect").Range("d3")
End Sub