## Copyright (c) 2001-2006, Andrew Straw. All rights reserved.
## Copyright (c) 2009, Florian Finkernagel. All rights reserved.

## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:

##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.

##     * Redistributions in binary form must reproduce the above
##       copyright notice, this list of conditions and the following
##       disclaimer in the documentation and/or other materials provided
##       with the distribution.

##     * Neither the name of the Florian Finkernagel nor the names of its
##       contributors may be used to endorse or promote products derived
##       from this software without specific prior written permission.

## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import unittest
import os
import numpy
from dataframe import DataFrame, DataFrameFrom2dArray, combine
from parsers import TabDialect, DF2CSV, DF2ARFF, DF2Excel, DF2TSV
from factors import Factor
import cPickle
import StringIO
import tempfile


class DataFrameTests(unittest.TestCase):
    def testCreation(self):
        u = DataFrame( { "Field1": [1, 2, 3], "Field2": ['abc', 'def', 'hgi']}, ['Field1', 'Field2'])
        self.assertEqual(u.columns_ordered, ['Field1', 'Field2'])
        self.assertEqual(u.get_row(0), {'Field1': 1, 'Field2': 'abc'})
        self.assertEqual(u.get_row(1), {'Field1': 2, 'Field2': 'def'})
        self.assertEqual(u.get_row(2), {'Field1': 3, 'Field2': 'hgi'})

    def testCreationAdditionalOrderFieldFails(self):
        def inner():
            u = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2', 'field3'])
        self.assertRaises(KeyError, inner)

    def testRBind(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [4, 5,6], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = a.rbind_copy(b)
        self.assertEqual(c.num_rows, 6)
        self.assertEqual(c.get_row(0), {'Field1': 1, 'Field2': 'abc'})
        self.assertEqual(c.get_row(1), {'Field1': 2, 'Field2': 'def'})
        self.assertEqual(c.get_row(2), {'Field1': 3, 'Field2': 'hgi'})
        self.assertEqual(c.get_row(3), {'Field1': 4, 'Field2': 'abc'})
        self.assertEqual(c.get_row(4), {'Field1': 5, 'Field2': 'def'})
        self.assertEqual(c.get_row(5), {'Field1': 6, 'Field2': 'hgi'})

    def test_combine(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [4, 5,6], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = combine([a, b])
        self.assertEqual(c.num_rows, 6)
        self.assertEqual(c.get_row(0), {'Field1': 1, 'Field2': 'abc'})
        self.assertEqual(c.get_row(1), {'Field1': 2, 'Field2': 'def'})
        self.assertEqual(c.get_row(2), {'Field1': 3, 'Field2': 'hgi'})
        self.assertEqual(c.get_row(3), {'Field1': 4, 'Field2': 'abc'})
        self.assertEqual(c.get_row(4), {'Field1': 5, 'Field2': 'def'})
        self.assertEqual(c.get_row(5), {'Field1': 6, 'Field2': 'hgi'})

    def testRBindMultiple(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [4, 5,6], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = a.rbind_copy(b, b)
        self.assertEqual(c.num_rows, 9)
        self.assertEqual(c.get_row(0), {'Field1': 1, 'Field2': 'abc'})
        self.assertEqual(c.get_row(1), {'Field1': 2, 'Field2': 'def'})
        self.assertEqual(c.get_row(2), {'Field1': 3, 'Field2': 'hgi'})
        self.assertEqual(c.get_row(3), {'Field1': 4, 'Field2': 'abc'})
        self.assertEqual(c.get_row(4), {'Field1': 5, 'Field2': 'def'})
        self.assertEqual(c.get_row(5), {'Field1': 6, 'Field2': 'hgi'})
        self.assertEqual(c.get_row(6), {'Field1': 4, 'Field2': 'abc'})
        self.assertEqual(c.get_row(7), {'Field1': 5, 'Field2': 'def'})
        self.assertEqual(c.get_row(8), {'Field1': 6, 'Field2': 'hgi'})

    def testRBindRequiresSameFields(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field1": [4, 5,6]}, ['Field1'])
            c = a.rbind_copy(b, b)
        self.assertRaises(KeyError, inner)

    def testCombineRequiresSameFields(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field1": [4, 5,6]}, ['Field1'])
            c = combine([a, b])
        self.assertRaises(KeyError, inner)

    def test_combine_promots_int_to_float(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [4.3, 5.5,6.6], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = combine([a, b])
        self.assertEqual(c.num_rows, 6)
        self.assertEqual(c.get_row(0), {'Field1': 1.0, 'Field2': 'abc'})
        self.assertEqual(c.get_row(1), {'Field1': 2.0, 'Field2': 'def'})
        self.assertEqual(c.get_row(2), {'Field1': 3.0, 'Field2': 'hgi'})
        self.assertEqual(c.get_row(3), {'Field1': 4.3, 'Field2': 'abc'})
        self.assertEqual(c.get_row(4), {'Field1': 5.5, 'Field2': 'def'})
        self.assertEqual(c.get_row(5), {'Field1': 6.6, 'Field2': 'hgi'})

    def testRBindSuceedsWithMaskedInts(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [1, None,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = a.rbind_copy(b)
        for x, y in zip(c.get_column_view('Field1').mask, [False, False, False, False, True, False]):
            self.assertEqual(x,y)

    def testCombineSuceedsWithMaskedInts(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [1, None,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        c = combine([a, b])
        for x, y in zip(c.get_column_view('Field1').mask, [False, False, False, False, True, False]):
            self.assertEqual(x,y)

    def testRBindSuceedsWithMaskedStrings(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc',None,'hgi']}, ['Field1','Field2'])
        c = a.rbind_copy(b)
        for x, y in zip(c.get_column_view('Field2').mask, [False, False, False, False, True, False]):
            self.assertEqual(x,y)

    def testRBindSuceedsWithMaskedUnicode(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": [u'abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field1": [1, 2,3], "Field2": [u'abc',None,'hgi']}, ['Field1','Field2'])
        c = a.rbind_copy(b)
        self.assertTrue(isinstance(c.get_value(2,'Field2'), unicode))
        for x, y in zip(c.get_column_view('Field2').mask, [False, False, False, False, True, False]):
            self.assertEqual(x,y)


    def insert_column_raises_on_duplicate_column(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        def inner():
            a.insert_column("Field1", [5,6,7])
        self.assertRaises(ValueError, inner)
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])


    def testCBindViews(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field3": [4, 5,6], "Field4": ['abc','def','hgi']})
        c = a.cbind_view(b)
        self.assertEqual(c.get_row(0), {'Field1': 1, 'Field2': 'abc', 'Field3': 4, 'Field4': 'abc'})
        a[2, "Field1"] = 55
        self.assertEqual(c[:, "Field1"][2],55)

    def testCBindRetainsOrder(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field3": [4, 5,6], "Field4": ['abc','def','hgi']}, ['Field3','Field4'])
        c = a.cbind_view(b)
        self.assertEqual(c.columns_ordered, ['Field1','Field2','Field3','Field4'])
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field2','Field1'])
        b = DataFrame( { "Field3": [4, 5,6], "Field4": ['abc','def','hgi']}, ['Field4','Field3'])
        c = a.cbind_view(b)
        self.assertEqual(c.columns_ordered, ['Field2','Field1','Field4','Field3'])

    def testCBindMultiple(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        b = DataFrame( { "Field3": [4, 5,6], "Field4": ['abc','def','hgi']})
        c = DataFrame( { "Field5": [7, 8,9]})
        d = a.cbind_view(b, c)
        self.assertEqual(d.get_row(0), {'Field1': 1, 'Field2': 'abc', 'Field3': 4, 'Field4': 'abc', 'Field5': 7})

    def testCBindRequiresSameNumberOfRows(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field3": [4, ], "Field4": ['abc']})
            c = a.cbind_view(b)
        self.assertRaises(ValueError, inner)

    def testCBindFailsOnIdenticallyNamedFields(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field3": [4, ], "Field2": ['abc']})
            c = a.cbind_view(b)
        self.assertRaises(ValueError, inner)

    def test_join_columns_on(self):
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field4": [22,11,33], "Field2": ['def','abc','hgi']}, ['Field4','Field2'])
            x = a.join_columns_on(b, 'Field2', 'Field2')
            self.assertTrue((x.get_column_view("Field4") == [11,22,33]).all())


    def test_join_columns_on_raises_on_duplicate_here(self):
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','abc']}, ['Field1','Field2'])
            b = DataFrame( { "Field4": [22,11,33], "Field2": ['def','abc','hgi']}, ['Field4','Field2'])
            def inner():
                x = a.join_columns_on(b, 'Field2', 'Field2')
            self.assertRaises(KeyError, inner)

    def test_join_columns_on_raises_on_duplicate_there(self):
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field4": [22,11,33], "Field2": ['def','abc','def']}, ['Field4','Field2'])
            def inner():
                x = a.join_columns_on(b, 'Field2', 'Field2')
            self.assertRaises(KeyError, inner)

    def test_join_columns_on_raises_on_unequal_keys(self):
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field4": [22,11,33], "Field2": ['def','abc','hgi']}, ['Field4','Field2'])
            def inner():
                x = a.join_columns_on(b, 'Field2', 'Field2')
            self.assertRaises(ValueError, inner) 

    def test_join_columns_on_raises_on_unequal_Lengths(self):
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi']}, ['Field1','Field2'])
            b = DataFrame( { "Field4": [22,11,33,44], "Field2": ['def','abc','thgi','shu']}, ['Field4','Field2'])
            def inner():
                x = a.join_columns_on(b, 'Field2', 'Field2')
            self.assertRaises(ValueError, inner) 

    def test_groupby(self):
        a = DataFrame( { "Field1": [1, 2,1], "Field2": ['shu','def','hgi']}, ['Field1','Field2'])
        b = list(a.groupby('Field1'))
        self.assertEqual(b[0][0], 1)
        self.assertTrue((b[0][1].get_column_view('Field2') == ['shu','hgi']).all())
        self.assertEqual(b[1][0], 2)
        self.assertTrue((b[1][1].get_column_view('Field2') == ['def']).all())


    def testInsertColumn(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        a.insert_column('test', [7.0,8.0,9.0])
        self.assertEqual(a.get_row(0), {'Field1': 1, 'Field2': 'abc', 'test': 7.0})
        self.assertTrue(isinstance(a.value_dict['test'], numpy.ndarray))

    def testInsertColumnRaisesOnInvalidLength(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
            a.insert_column('test', [7.0,8.0])
        self.assertRaises(ValueError, inner)

    def testDropColumn(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        a.drop_column("Field1")
        self.assertEqual(a.get_row(0), {'Field2': 'abc'})

    def testDropColumnExcept(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        a.drop_all_columns_except("Field1")
        self.assertEqual(a.get_row(0), {'Field1': 1})

    def testDataframeEquality(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a, a)
        b = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a, b)
        c = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field3','Field2', 'Field1'])
        self.assertEqual(a, c)
        self.assertEqual(b, c)

    def testDataFrameComparisons(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        a1 = a[:,"Field1"] == 2
        self.assertEqual(a1[0], False)
        self.assertEqual(a1[1], True)
        self.assertEqual(a1[2], False)
        a2 = a[:,"Field2"] == 'def'
        self.assertEqual(a2[0], False)
        self.assertEqual(a2[1], True)
        self.assertEqual(a2[2], False)
        a3 = a[:,"Field2"] == None
        self.assertEqual(a3[0], False)
        self.assertEqual(a3[1], False)
        self.assertEqual(a3[2], False)


    def testDataFrameInequalityIfDifferentColumns(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        b = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        self.assertNotEqual(a, b)

    def testDataFrameInequalityIfDifferentRowLengths(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        b = DataFrame( { "Field1": [1, 2,3,4], "Field2": ['abc','def','hgi','jkl'], 'Field3': [7.0,8.0,9.0,10.0]}, ['Field1','Field2', 'Field3'])
        self.assertNotEqual(a, b)
    def testDataFrameInequalityIfDifferentValues(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        b = DataFrame( { "Field1": [1, 2,4], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertNotEqual(a, b)

    def testDataFrameInequalityIfSameValuesDifferentOrder(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        b = DataFrame( { "Field1": [3, 2,1], "Field2": ['hgi','def','abc'], 'Field3': [9.0,8.0,7.0]}, ['Field1','Field2', 'Field3'])
        self.assertNotEqual(a, b)

    def testDataFrameNotEqualWithOtherValue(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        a1 = a[:,"Field1"] != 2
        self.assertEqual(a1[0], True)
        self.assertEqual(a1[1], False)
        self.assertEqual(a1[2], True)

        a1 = a[:,"Field2"] != 'def'
        self.assertEqual(a1[0], True)
        self.assertEqual(a1[1], False)
        self.assertEqual(a1[2], True)

    def testDim(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a.dim(), (3,3))

    def testShape(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6],  'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1', 'Field3'])
        self.assertEqual(a.shape, (6,2))
        self.assertEqual(a.shape, a.dim())

    def testShapeRaisesOnSet(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6],  'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1', 'Field3'])
            a.shape = (5,5)
        self.assertRaises(ValueError, inner)

    def testShapeRaisesOnDel(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6],  'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1', 'Field3'])
            del a.shape 
        self.assertRaises(ValueError, inner)

    def testDataFrameFromListOfDicts(self):
        input = [
            {'Field1': 2,
             'Field2': 3.0},
            {'Field1': 22,
             'Field2': 33.33},
            {'Field1': 4,
             'Field2': 5.55}
        ]
        df = DataFrame(input, ['Field1','Field2'])
        self.assertEqual(df.columns_ordered, ['Field1','Field2'])

    def test_impose_order_raises_on_invalid_column(self):
        input = [
            {'Field1': 2,
             'Field2': 3.0},
            {'Field1': 22,
             'Field2': 33.33},
            {'Field1': 4,
             'Field2': 5.55}
        ]
        df = DataFrame(input, ['Field1','Field2'])
        self.assertEqual(df.columns_ordered, ['Field1','Field2'])
        df.impose_partial_column_order(["Field2","Field1"])
        def inner():
            df.impose_partial_column_order(("Field2","FieldX"))
        self.assertRaises(KeyError, inner)

    def test_simple_melt(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'], 'Field3': [10,20,30]}, ['Field1','Field2'])
        x = a.melt(["Field2"], ["Field1",'Field3'], 'source','value')
        supposed_melted = DataFrame([
            {"Field2": 'shu', 'source': 'Field1', 'value': 1},
            {"Field2": 'shu', 'source': 'Field3', 'value': 10},
            {"Field2": 'def', 'source': 'Field1', 'value': 2},
            {"Field2": 'def', 'source': 'Field3', 'value': 20},
            {"Field2": 'hgi', 'source': 'Field1', 'value': 3},
            {"Field2": 'hgi', 'source': 'Field3', 'value': 30}])
        self.assertEqual(x,supposed_melted)

    def test_simple_aggregate(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'], 'Field3': [10,20,30]}, ['Field1','Field2'])
        x = a.melt(["Field2"], ["Field1",'Field3'], 'source','value')
        y = x.aggregate(['Field2'], lambda d: {'sum': sum(d.get_column_view('value'))})
        supposed_aggregated = DataFrame([
            {'Field2': 'def', 'sum': 22},
            {'Field2': 'hgi', 'sum': 33},
            {'Field2': 'shu', 'sum': 11},
            ])
        self.assertEqual(y, supposed_aggregated)



    def test_level_melt(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'], 'Field3': [10,20,30]}, ['Field1','Field2'])
        a.turn_into_level('Field2')
        x = a.melt(["Field2"], ["Field1",'Field3'], 'source','value')
        supposed_melted = DataFrame([
            {"Field2": 'shu', 'source': 'Field1', 'value': 1},
            {"Field2": 'shu', 'source': 'Field3', 'value': 10},
            {"Field2": 'def', 'source': 'Field1', 'value': 2},
            {"Field2": 'def', 'source': 'Field3', 'value': 20},
            {"Field2": 'hgi', 'source': 'Field1', 'value': 3},
            {"Field2": 'hgi', 'source': 'Field3', 'value': 30}])
        supposed_melted.turn_into_level('Field2', a.value_dict['Field2'].levels)
        self.assertEqual(x,supposed_melted)

    def test_melt_drops_unspecified(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'],"Field4": ['a','b','c'], 'Field3': [10,20,30]}, ['Field1','Field2'])
        x = a.melt(["Field2"], ["Field1",'Field3'], 'source','value')
        supposed_melted = DataFrame([
            {"Field2": 'shu', 'source': 'Field1', 'value': 1},
            {"Field2": 'shu', 'source': 'Field3', 'value': 10},
            {"Field2": 'def', 'source': 'Field1', 'value': 2},
            {"Field2": 'def', 'source': 'Field3', 'value': 20},
            {"Field2": 'hgi', 'source': 'Field1', 'value': 3},
            {"Field2": 'hgi', 'source': 'Field3', 'value': 30}])
        self.assertEqual(x,supposed_melted)

    def test_types(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'],"Field4": [3,'b','c'], 'Field3': [10.5,20,30],
            'Field5': ['shu', unicode('sha'), u'rah']})
        t = {}
        for name, typ in a.types():
            t[name] = typ
        self.assertEqual(t['Field1'], numpy.int32)
        self.assertEqual(t['Field2'], numpy.object)
        self.assertEqual(type(a.get_column_view('Field2')[0]), str)
        self.assertEqual(t['Field4'], numpy.object)
        self.assertEqual(type(a.get_column_view('Field4')[0]), str)
        self.assertEqual(t['Field3'], numpy.float)
        self.assertEqual(t['Field5'], numpy.object)
        self.assertEqual(type(a.get_column_view('Field5')[0]), unicode)



    def test_melt_two_id_columns(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['shu','def','hgi'],"Field4": ['a','a','c'], 'Field3': [10,20,30]}, ['Field1','Field2'])
        x = a.melt(["Field2",'Field4'], ["Field1",'Field3'], 'source','value')
        supposed_melted = DataFrame([
            {"Field2": 'shu', 'Field4': 'a', 'source': 'Field1', 'value': 1},
            {"Field2": 'shu', 'Field4': 'a', 'source': 'Field3', 'value': 10},
            {"Field2": 'def', 'Field4': 'a', 'source': 'Field1', 'value': 2},
            {"Field2": 'def', 'Field4': 'a', 'source': 'Field3', 'value': 20},
            {"Field2": 'hgi', 'Field4': 'c', 'source': 'Field1', 'value': 3},
            {"Field2": 'hgi', 'Field4': 'c', 'source': 'Field3', 'value': 30}])
        self.assertEqual(x,supposed_melted)
class DataFrameAccessorTests(unittest.TestCase):

    def testGetRow(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame ( { "Field1": [2], "Field2": ['def'], 'Field3': [8.0]}, ['Field1', 'Field2', 'Field3'])
        self.assertEqual(a[1], should)

    def testGetLastRow(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame ( { "Field1": [3], "Field2": ['hgi'], 'Field3': [9.0]}, ['Field1', 'Field2', 'Field3'])
        self.assertEqual(a[-1], should)

    def testGetRowsSliced(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [1, 2], "Field2": ['abc','def'], 'Field3': [7.0,8.0]}, ['Field1','Field2', 'Field3'])

        self.assertEqual(a[0:2], should)

    def testGetRowsSlicedSpaced(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [1, 3,5], "Field2": ['abc','hgi','mno'], 'Field3': [7.0,9.0,11.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a[0:8:2], should)

    def testGetRowsReordered(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [3, 2,1], "Field2": ['hgi','def','abc'], 'Field3': [9.0,8.0,7.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a[(2, 1,0),:], should)

    def testGetRowsReorderedRaisesIfYouDontTellRowsExplicitly(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
            should = DataFrame( { "Field1": [3, 2,1], "Field2": ['hgi','def','abc'], 'Field3': [9.0,8.0,7.0]}, ['Field1','Field2', 'Field3'])
            a[(2, 1,0)]
        self.assertRaises(ValueError, inner)

    def testGetSpecificCell(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( {"Field2": ['def'] }, ['Field2'])
        self.assertEqual(a[1, "Field2"],should)
        self.assertEqual(a[1, 1],should)

    def testGetColumn(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['abc', 'def','hgi']}, ['Field2'])
        self.assertEqual(a[:, "Field2"],should)
        self.assertEqual(a[:, 1],should)

    def testGetColumnViewNumeric(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field3', 'Field2'])
        should = numpy.array(['abc', 'def','hgi'])
        self.assertTrue((a.get_column_view(2) == should).all())

    def testGetLastColumn(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field3', 'Field2'])
        should = DataFrame( { "Field2": ['abc', 'def','hgi']}, ['Field2'])
        self.assertEqual(a[:, -1],should)

    def testGetColumnSliced(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( {"Field1": [1, 2,3],  "Field2": ['abc','def','hgi']}, ['Field1','Field2'])
        self.assertEqual(a[:, 0:2],should)
        self.assertEqual(a[:, 0:2].columns_ordered, should.columns_ordered)

    def testGetColumnSubset(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( {"Field1": [1, 2,3],  "Field2": ['abc','def','hgi']}, ['Field2','Field1'])
        self.assertEqual(a[:, ("Field2","Field1")],should)
        self.assertEqual(a[:, ("Field2","Field1")].columns_ordered, should.columns_ordered)
        self.assertEqual(a[:, (1,0)],should)
        self.assertEqual(a[:, (1,0)].columns_ordered, should.columns_ordered)

    def testGetRectangular(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [1, 2,5,6], 'Field3': [7.0,8.0,11.0,12.0]}, ['Field1','Field3'])
        self.assertEqual(a[(0, 1,4,5),("Field1","Field3")],should)

    def testGetRectangularNegativeIndices(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [1, 2,5,6], 'Field3': [7.0,8.0,11.0,12.0]}, ['Field1','Field3'])
        self.assertEqual(a[(0, 1,-2,-1),("Field1","Field3")],should)
        self.assertEqual(a[(0, 1,-2,-1),(0,2)],should)
        self.assertEqual(a[(0, 1,-2,-1),(0,-1)],should)


    def testGetBooleanRow(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame ( { "Field1": [2], "Field2": ['def'], 'Field3': [8.0]}, ['Field1', 'Field2', 'Field3'])
        self.assertEqual(a[(False, True,False),:], should)


    def testGetBooleanRows(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(a[(True, False,True,False,False,False),:],should)
        def inner():
            self.assertEqual(a[(True, False,True,False,False,False)],should)
        self.assertRaises(ValueError, inner)

    def testGetColumnBooleans(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['abc', 'def','hgi','jkl','mno','pqr'] }, ['Field2'])
        self.assertEqual(a[:, (False,True,False)], should)
        self.assertEqual(a[:, [x.find('2') != -1 for x in a.columns_ordered]], should)

    def testGetBooleanRectangular(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['hgi']}, ['Field2'])
        self.assertEqual(a[(False, False,True,False,False,False),(False,True,False)], should)

    def testGetNoRowBoolCol(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['hgi']}, ['Field2'])
        self.assertEqual(a[2, (False,True,False)], should)

    def testGetTupleRowBoolCol(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['hgi', 'jkl']}, ['Field2'])
        self.assertEqual(a[(2, 3),(False,True,False)], should)
        self.assertEqual(a[2:4, (False,True,False)], should)

    def testGetBooleanRowNumpyBool(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame ( { "Field1": [2], "Field2": ['def'], 'Field3': [8.0]}, ['Field1', 'Field2', 'Field3'])
        self.assertEqual(a[numpy.array((False, True,False)),:], should)

    def testGetBooleanRectangularNumpyBools(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['abc','def','hgi','jkl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        should = DataFrame( { "Field2": ['hgi']}, ['Field2'])
        self.assertEqual(a[numpy.array((False, False,True,False,False,False)),numpy.array((False,True,False))], should)
    def testWhere(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a.where(lambda row: len(row['Field2']) < 3)), list(numpy.array((True, False,False,True,False,False))))

    def testGreaterOrEqual(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a[:, "Field1"] >= 4), list(numpy.array((False,False,False,True,True,True))))

    def testGreaterOrEqualRaisesIfOneMoreThanOneColumnDataFrame(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            self.assertEqual(list(a >= 4), list(numpy.array((False, False,False,True,True,True))))
        self.assertRaises(ValueError, inner)

    def testGreater(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a[:, "Field1"] > 3), list(numpy.array((False,False,False,True,True,True))))

    def testGreaterRaisesIfOneMoreThanOneColumnDataFrame(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            self.assertEqual(list(a > 4), list(numpy.array((False, False,False,True,True,True))))
        self.assertRaises(ValueError, inner)

    def testLess(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a[:, "Field1"] < 3), list(numpy.array((True,True,False,False,False,False))))

    def testLessRaisesIfOneMoreThanOneColumnDataFrame(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a < 4
        self.assertRaises(ValueError, inner)
        
       
    def testLessOrEqual(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a[:, "Field1"] <= 3), list(numpy.array((True,True,True,False,False,False))))

    def testLessOrEqualRaisesIfOneMoreThanOneColumnDataFrame(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a <= 4
        self.assertRaises(ValueError, inner)
        
    def testEqual(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(list(a[:, "Field2"] == 'hgi'), list(numpy.array((False,False,True,False,False,False))))

    def testEqualRaisesIfOneMoreThanOneColumnDataFrame(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['ab','def','hgi','jl','mno','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a == 4
        self.assertRaises(ValueError, inner)

    def testSortBySingleField(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a = a.sort_by('Field1')
        self.assertEqual(list(a.get_column(0)), [1, 2,3,4,5,6])
        self.assertEqual(list(a.get_column(1)), ['def', 'ab','jl','ab','hgi','pqr'])
        
    def test_sort_by_invalid_field_raises(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a = a.sort_by('FieldX')
        self.assertRaises(KeyError, inner)
    
    def test_sort_by_invalid_field_raises2(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a = a.sort_by('FieldX', True)
        self.assertRaises(KeyError, inner)

    def test_sort_by_invalid_field_raises3(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a = a.sort_by(('Field1', 'FieldX'), (True, False))
        self.assertRaises(KeyError, inner)
  
    def testSortBySingleFieldReverse(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a = a.sort_by('Field1', False)
        self.assertEqual(list(a.get_column(0)), [6, 5,4,3,2,1])
        self.assertEqual(list(a.get_column(1)), ['pqr', 'hgi','ab','jl','ab','def'])

    def testSortBySingleFieldStable(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a = a.sort_by('Field2') # should be a stable sort, if I understand python correctly
        self.assertEqual(list(a.get_column(1)), ['ab', 'ab','def','hgi','jl','pqr'])
        self.assertEqual(list(a.get_column(0)), [2, 4,1,5,3,6])

    def testSortByTwoFields(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a = a.sort_by(('Field2', 'Field1'), ascending=(False,True))
        self.assertEqual(list(a.get_column(1)), ['pqr', 'jl','hgi','def','ab','ab'])
        self.assertEqual(list(a.get_column(0)), [6, 3,5,1,2,4])

    def testSortRaisesIfAscendingIsntSpecificedCorrectly(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a = a.sort_by(('Field2', 'Field1'), ascending=False)
        self.assertRaises(ValueError, inner)

    def testGetAsListOfArrays(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [numpy.ma.array((1,3), dtype=numpy.int32),
                  numpy.ma.array(('abc','hgi'), dtype='S3'),
                  numpy.ma.array((7.0,9.0), dtype=numpy.float)
                 ]
        was = df.get_as_list_of_arrays_view()
        for i in xrange(0 ,len(was)):
            for t in xrange(0,len(was[i])):
                self.assertEqual(should[i][t], was[i][t])

    def testGetAsNestedList(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [ 
                    [1, 'abc', 7.0],
                    [3, 'hgi', 9.0]
                 ]
        was = df.get_as_list_of_lists()
        for i in xrange(0 ,len(was)):
            for t in xrange(0,len(was[i])):
                self.assertEqual(should[i][t], was[i][t])

    def testGetAsListedAndSetItemPlayTogether(self):
        df_one = DataFrame({"A": (1, 2), "B": (3, 4)})
        df_two = DataFrame({"C": (2, 4), 'D': (6, 8)})
        def inner():
            df_one[:] =  df_two
        self.assertRaises(ValueError, inner)

        df_one[:]  = df_two.get_as_list_of_lists()
        should = DataFrame({"A": (2, 4), "B": (6, 8) })
        self.assertEqual(should, df_one)

    def testGetByGiaganticbooleanArray(self):
        """This was to debug some obscure behaviour that 
        in the end showed itself much sooner than anticipated
        in the number of rows"""
        upperLimit = 6000
        a = DataFrame({"Field1": range(0, upperLimit)})
        selector = numpy.zeros((upperLimit, ),dtype=numpy.bool)
        selector[1] = True
        selector[99] = True
        x = a[selector, :]
        self.assertEqual(x[0, 'Field1'],1)
        self.assertEqual(x[1, 'Field1'],99)
        selector = a[:, "Field1"] >= 500
        b = a[selector, :]
        self.assertEqual(b.num_rows, upperLimit - 500)

    def testStraightIterRaises(self):
        def inner():
            df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
            itered = False
            for p in df:
                itered = True
        self.assertRaises(ValueError, inner)

    def testStraightIterWorksOnSingleColumnDataFrames(self):
        df = DataFrame( { "Field1": [1, 3],} )
        itered = False
        for p in df:
            itered = True
        self.assertTrue(itered)

    def testIterValuesColumnsFirst(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [1,3, 'abc','hgi',7.0,9.0]
        was = []
        for k in df.iter_values_columns_first():
            was.append(k)
        self.assertEqual(should,was)

    def testIterValuesRowsFirst(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [1,'abc',7.0, 3, 'hgi',9.0]
        was = []
        for k in df.iter_values_rows_first():
            was.append(k)
        self.assertEqual(should,was)

    def testIterColumns(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [numpy.ma.array((1,3), dtype=numpy.int32),
                  numpy.ma.array(('abc','hgi'), dtype='S3'),
                  numpy.ma.array((7.0,9.0), dtype=numpy.float)
                 ]
        was = []
        for column in df.iter_columns():
            was.append(column)
        for i in xrange(0, len(should)):
            for t in xrange(0, len(should[i])):
                self.assertEqual(should[i][t], was[i][t])
        self.assertNotEqual([1,2,3],[2,3,1])

    def testIterRows(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        should = [
            {"Field1": 1, "Field2": 'abc', 'Field3': 7.0},
            {"Field1": 3, "Field2": 'hgi', 'Field3': 9.0},
        ]
        was = []
        for row in df.iter_rows():
            was.append(row)
        self.assertEqual(should, was)

    def testGetColumns(self):
        df = DataFrame( { "Field1": [1, 3], "Field2": ['abc','hgi'], 'Field3': [7.0,9.0]}, ['Field1','Field2', 'Field3'])
        self.assertEqual(["Field1","Field2","Field3"], df.get_column_names())


class DataFrameCSVTest(unittest.TestCase):
    def testReadWrite(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        o = open("test.txt", "wb")
        conv.write(a,o)
        o.close()
        o = open("test.txt", "rb")
        b = conv.read(o)
        o.close()
        os.unlink('test.txt')
        self.assertEqual(a, b)
    
    def testReadWrite_handling_quotes_single_column(self):
        conv = DF2CSV()
        a = DataFrame( { "Field2": ['def','ab','jl','ab','h gi','pqr']})
        o = open("test.txt", "wb")
        conv.write(a,o)
        o.close()
        o = open("test.txt", "rb")
        b = conv.read(o, handle_quotes=True)
        o.close()
        #os.unlink('test.txt')
        self.assertEqual(a, b)

    def testReadWriteFilename(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        conv.write(a, 'test.txt')
        b = conv.read("test.txt")
        os.unlink('test.txt')
        self.assertEqual(a, b)

    def testReadWriteFilenameGzip(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        conv.write(a, 'test.txt.gz')
        b = conv.read("test.txt.gz")
        os.unlink('test.txt.gz')
        self.assertEqual(a, b)

    def testTypeHints(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        conv.write(a,'test.txt.gz')
        b = conv.read("test.txt.gz", type_hints = {'Field1': numpy.float32})
        os.unlink('test.txt.gz')
        self.assertEqual(b.value_dict['Field1'].dtype, numpy.float32)

    def testConvertReadingOfMaskedValues(self):
        conv = DF2CSV()
        o = open("test.txt", 'wb')
        o.write("field1\tfield2\n")
        o.write("1.0\t2\n")
        o.write("NA\tNA\n")
        o.write("3\t3\n")
        o.close()
        b =conv.read('test.txt', na_text="NA", dialect=TabDialect)
        os.unlink('test.txt')
        shouldField1 = numpy.ma.array([1.0, numpy.nan, 3.0 ], dtype=numpy.double)
        shouldField1.mask = (False, False, False)
        shouldField2 = numpy.ma.array([2, numpy.nan, 3], dtype=numpy.double)
        shouldField2.mask = (False, False, False)
        a = DataFrame( {"field1": shouldField1, 'field2': shouldField2})
        #Gotcha. nans in an int column automagically boost them to float!
        self.assertEqual(b.value_dict['field2'].dtype, numpy.float64)
        self.assertEqual(a, b)

    def testReadWriteWithRowNames(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'], ["alpha","beta","gamma","delta","epsilon",'zeta'])
        o = open("test.txt", "wb")
        conv.write(a,o)
        o.close()
        o = open("test.txt", "rb")
        b = conv.read(o, has_row_names=True)
        o.close()
        os.unlink('test.txt')
        self.assertEqual(a, b)

    def testReadWriteWithRowNamesFieldName(self):
        conv = DF2CSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','abx','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'], ["alpha","beta","gamma","delta","epsilon",'zeta'])
        o = open("test.txt", "wb")
        conv.write(a,o)
        o.close()
        o = open("test.txt", "rb")
        b = conv.read(o, has_row_names="Field2")
        o.close()
        os.unlink('test.txt')
        a.set_column("Row",a.row_names)
        a.row_names = a[:,"Field2"] 
        a.drop_column("Field2")
        self.assertEqual(a, b)

    def testTSVEmtyFirstColumn(self):
        conv= DF2TSV()
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','','jl','abx','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field2','Field1', 'Field3'])
        o = open("test.txt", "wb")
        conv.write(a,o)
        o.close()
        o = open("test.txt", "rb")
        b = conv.read(o) #note the lack of 'handle_quotes'
        o.close()
        self.assertEqual(a, b)



class DataFrameSharedDataSemanticTests(unittest.TestCase):
    """Unlike R Dataframes the descendands of one of my Dataframes share their data.
    Which also means that sort will lead to trouble..."""

    def testTypeGuestimationWorksInt(self):
        a = DataFrame ( {"one": [1, 2,3,4] })
        self.assertEqual(a.get_column('one').dtype, numpy.dtype('int32'))

    def testTypeGuestimationWorksFloat(self):
        a = DataFrame ( {"one": [1.0, 2.0,3.0,4.0] })
        self.assertEqual(a.get_column('one').dtype, numpy.float)

    def testTypeGuestimationWorksMixed(self):
        a = DataFrame ( {"one": [1, 2.0,3.0,4.0] })
        self.assertEqual(a.get_column('one').dtype, numpy.float)

    def testTypeGuestimationWorksBool(self):
        a = DataFrame ( {"one": [True, False,True] })
        self.assertEqual(a.get_column('one').dtype, numpy.bool)
    
    def testTypeGuestimationWorksStr(self):
        a = DataFrame ( {"one": ["Shu", "ShAAA","s"] })
        self.assertEqual(a.get_column('one').dtype, numpy.dtype('object'))

    #def testTypeGuestimationRaisesMixed(self):
        #def inner():
            #a = DataFrame ( {"one": [True, "ShAAA","s",2] })
        #self.assertRaises(ValueError, inner)

    #def testTypeGuestimationRaisesMixed2(self):
        #def inner():
            #a = DataFrame ( {"one": ["ShAAA", "s",2,2.0] })
        #self.assertRaises(ValueError, inner)

    def testTypeGuestimationWorksObjects(self):
        a = DataFrame ( {"one": [["ShAAA"], ["s"],[2]] })
        self.assertEqual(a.get_column('one').dtype, numpy.object)

    def testTypeGuestimatorHandlesNumpysCorrectly(self):
        a = DataFrame ( {"one": numpy.array([1, 2,3,4,5]) })
        self.assertEqual(a.get_column('one').dtype, numpy.int64)

    def testSubselectionsDontAlwaysShareData(self):
        """I know this is a weak test...but I guess the whole confusion
        stems from numpy in the first place. Anyhow, this does a copy"""
        a = DataFrame ( {"one": numpy.array([1, 2,3,4,5]) })
        b = a[1:5]
        a[2, "one"] = 66
        #a.get_column("one")[2] = 66
        self.assertEqual(b.get_value(0, 'one'),2)

class DataFrameManipulationTests(unittest.TestCase):

    def testSetValueSingleCell(self):
        a = DataFrame ( {"one": numpy.array([1, 2,3,4,5]) })
        self.assertEqual(a[1, "one"], 2)
        a[1, 'one'] = 55
        self.assertEqual(a[1, "one"], 55)

    def testSetValueSingleColumn(self):
        a = DataFrame ( {"one": numpy.array([1, 2,3,4,5]) })
        self.assertEqual(a[1, "one"], 2)
        a[:, 'one'] = 55
        self.assertEqual(a[0, "one"], 55)
        self.assertEqual(a[1, "one"], 55)
        self.assertEqual(a[2, "one"], 55)
        self.assertEqual(a[3, "one"], 55)
        self.assertEqual(a[4, "one"], 55)

    def testSetSingleColumnFromOtherDataFrameWithOneColumnButDifferentName(self):
        a = DataFrame ( {"one": numpy.array([1, 2,3,4,5]) })
        b = DataFrame ( {"two": numpy.array([10, 11,12,13,14]) })
        self.assertEqual(a[1, "one"], 2)
        a[:, 'one'] = b
        self.assertEqual(a[0, "one"], 10)
        self.assertEqual(a[1, "one"], 11)
        self.assertEqual(a[2, "one"], 12)
        self.assertEqual(a[3, "one"], 13)
        self.assertEqual(a[4, "one"], 14)

    def testSetSingleRowFromDict(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[2, :] = {"Field1": 55, "Field2": "shu", "Field3": 66.0}
        self.assertEqual(a[2, "Field1"], 55)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 66.0)

    def testSetSingleRowFromDataFrame(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[2, :] = DataFrame({"Field1": [55], "Field2": ["shu"], "Field3": [66.0]})
        self.assertEqual(a[2, "Field1"], 55)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 66.0)

    def testSetSingleRowFromTuple(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[2, :] = ( 55, "shu", 66.0)
        self.assertEqual(a[2, "Field1"], 55)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 66.0)

    def testSetSingleRowFromTupleRaisesOnInvalidFieldLength(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[2, :] = ( 55, "shu")
        self.assertRaises(ValueError, inner)

    def testSetSingleRowFromTupleRaisesOnPassingStrToInt(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[2, :] = ( "shu", 43, 66.0)
        self.assertRaises(ValueError, inner)

    def testSetSingleRowRaisesOnMissingField(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[2, :] = DataFrame({"Field1": [55],  "Field3": [66.0]})
        self.assertRaises(ValueError, inner)

    def testSetSingleRowRaisesOnAdditonalField(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[2, :] = DataFrame({"Field1": [55], "Field2": ["shu"], "Field3": [66.0], "Field4": [12]})
        self.assertRaises(ValueError, inner)

    def testSetMultipleRowsFromListOfTuples(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[2:4, :] = [( 55, "shu", 66.0),( 55, "shu", 66.0)]
        self.assertEqual(a[2, "Field1"], 55)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 66.0)
        self.assertEqual(a[3, "Field1"], 55)
        self.assertEqual(a[3, "Field2"], "shu")
        self.assertEqual(a[3, "Field3"], 66.0 )

    def testSetMultipleRowsFromDict(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[(2, 4),:] = {"Field1": [55,66], "Field2": ["shu",'sha'], "Field3": [67.0,77]}
        self.assertEqual(a[2, "Field1"], 55)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 67.0)
        self.assertEqual(a[4, "Field1"], 66)
        self.assertEqual(a[4, "Field2"], "sha")
        self.assertEqual(a[4, "Field3"], 77.0)

    def testSetMultipleRowsFromDictRaisesOnUnequalNumberOfRows(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[2:3, :] = {"Field1": [55,66], "Field2": ["shu",'sha'], "Field3": [67.0,77]}
        self.assertRaises(ValueError, inner)

    def testSetRectangularTwoColumnsOneRow(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[2, ("Field2","Field3")] = DataFrame ({ "Field2": ["shu"], "Field3": [44]})
        self.assertEqual(a[2, "Field1"], 3)
        self.assertEqual(a[2, "Field2"], "shu")
        self.assertEqual(a[2, "Field3"], 44)

    def testSetRectangularTwoColumnsMultipleRowsBoolean(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
        a[(False, True,False,True,False,True),("Field2","Field3")] = DataFrame ({ "Field2": ["a",'b','c'], "Field3": [11,22,33]})
        self.assertEqual(a[1, "Field1"], 2)
        self.assertEqual(a[1, "Field2"], "a")
        self.assertEqual(a[1, "Field3"], 11)
        self.assertEqual(a[3, "Field1"], 4)
        self.assertEqual(a[3, "Field2"], "b")
        self.assertEqual(a[3, "Field3"], 22)
        self.assertEqual(a[5, "Field1"], 6)
        self.assertEqual(a[5, "Field2"], "c")
        self.assertEqual(a[5, "Field3"], 33)

    def testSetRectangularTwoColumnsMultipleRowsBooleanRaisesOnMissingRow(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[(False, True,False,True,False,True),("Field2","Field3")] = DataFrame ({ "Field2": ["a",'b',], "Field3": [11,22]})
        self.assertRaises(ValueError, inner)

    def testSetRectangularTwoColumnsMultipleRowsBooleanRaisesOnAdditionalRow(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[(False, True,False,True,False,True),("Field2","Field3")] = DataFrame ({ "Field2": ["a",'b','c','d'], "Field3": [11,22,33,44]})
        self.assertRaises(ValueError, inner)

    def testSetRectangularTwoColumnsMultipleRowsBooleanRaisesOnAdditionalColumn(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[(False, True,False,True,False,True),("Field2","Field3")] = DataFrame ({ "Field2": ["a",'b','c'], "Field3": [11,22,33], "Field1": [99,100,101]})
        self.assertRaises(ValueError, inner)
    def testSetRectangularTwoColumnsMultipleRowsBooleanRaisesOnMissingColumn(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            a[(False, True,False,True,False,True),("Field2","Field3")] = DataFrame ({ "Field2": ["a",'b','c']})
        self.assertRaises(ValueError, inner)

    def testMultiplicationSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,12], 'Field3': [14,16,18,20,22,24]})
        c = a * 2
        self.assertEqual(b, c)

    def testDivisionSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,12], 'Field3': [14,16,18,20,22,24]})
        c = b / 2
        self.assertEqual(a, c)

    def testAdditionSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [51, 52,53,54,55,56], 'Field3': [57,58,59,60,61,62]})
        c = a + 50
        self.assertEqual(b, c)

    def testSubstractonSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [51, 52,53,54,55,56], 'Field3': [57,58,59,60,61,62]})
        c = b - 50
        self.assertEqual(a, c)

    def testTrueDivSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6.5], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.5]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,13], 'Field3': [14,16,18,20,22,25]})
        c = b / 2.0
        self.assertEqual(a, c)

    def testFloorDivSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6.0], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,13], 'Field3': [14,16,18,20,22,25]})
        c = b // 2.0
        self.assertEqual(a, c)

    def testModSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6.0], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [1, 0,1,0,1,0], 'Field3': [1,0,1,0,1,0]})
        c = a % 2
        self.assertEqual(b, c)

    def testMultiplicationSingleValueJustOneColumn(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,12], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        a[:, "Field1"] *= 2
        self.assertEqual(b, a)

    def testDivisionSingleCell(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [1, 2,1,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        a[(2, ),"Field1"] /=  2
        self.assertEqual(b, a)

    def testAdditionMultipleRowsSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [1, 2,5,4,5,8], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        a[(2, 5),"Field1"] +=  2
        self.assertEqual(b, a)

    def testSubstractionRectangularSingleValue(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0], "Field2": ['def','ab','jl','ab','hgi','pqr'],})
        b = DataFrame( { "Field1": [1, 2,1,4,5,4], 'Field3': [7.0,8.0,7.0,10.0,11.0,10.0], "Field2": ['def','ab','jl','ab','hgi','pqr'],})
        a[(2, 5),("Field1","Field3")] -=  2
        self.assertEqual(b, a)

    def testAdditionCompleteFrame(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [2, 4,6,8,10,12], 'Field3': [14,16,18,20,22,24]})
        c = a + a
        self.assertEqual(b, c)

    def testMultiplicationBooleanSubset(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [1, 2,9,16,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        a[(False, False,True,True,False,False),("Field1")] *= DataFrame({"Field1": [3,4]})
        self.assertEqual(b, a)

    def testAbs(self):
        a = DataFrame( { "Field1": [-1, 2,-3,4,-5,-6], 'Field3': [7.0,-8.0,9.0,-10.0,11.0,12.0]})
        b = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]})
        c = abs(a)
        self.assertEqual(c,b)


    def testCbindingAndMultiplication(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        avg = (a[:, "Field1"] + a[:,"Field3"]) / 2
        self.assertEqual(avg, DataFrame({"(Field1+Field3)": [4, 5, 6, 7, 8, 9]}))
        avg.rename_column(0, 'avg')
        b = a.cbind_view(avg)
        self.assertEqual(b.columns_ordered, ['Field1', 'Field3', 'avg'])
        a[0, 0] = 5
        self.assertEqual(b[0, 'Field1'],5)

    def testRenamingByName(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.rename_column('Field1', 'FieldX')
        self.assertEqual(a.columns_ordered, ['FieldX', 'Field3'])
        self.assertTrue('FieldX' in a.value_dict)
        self.assertFalse('Field1' in a.value_dict)
        self.assertTrue('Field3' in a.value_dict)

    def testRenamingByNameRaisesOnDuplicate(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        def inner():
            a.rename_column('Field1', 'Field3')
        self.assertRaises(ValueError, inner)

    def testRenamingByPosition(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.rename_column(0, 'FieldX')
        self.assertEqual(a.columns_ordered, ['FieldX', 'Field3'])
        self.assertTrue('FieldX' in a.value_dict)
        self.assertFalse('Field1' in a.value_dict)
        self.assertTrue('Field3' in a.value_dict)

    def testSetColumnRaisesOnTooFew(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
            a.set_column("Field1",[0,])
        self.assertRaises(ValueError, inner)

    def testSetColumnRaisesOnTooMany(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
            a.set_column("Field1",[1, 2,3,4,5,6, 7])
        self.assertRaises(ValueError, inner)

    def testSetColumnCorrect(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.set_column("Field1",[1, 2,3,4,5,6][::-1])
        self.assertEqual(a.get_value(0,0),6)
        self.assertEqual(a.get_value(1,0),5)
        self.assertEqual(a.get_value(2,0),4)
        self.assertEqual(a.get_value(3,0),3)
        self.assertEqual(a.get_value(4,0),2)
        self.assertEqual(a.get_value(5,0),1)

    def testSetColumnCorrectNewColumn(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.set_column("FieldX",[1, 2,3,4,5,6][::-1])
        self.assertEqual(a.get_value(0,"FieldX"),6)
        self.assertEqual(a.get_value(1,"FieldX"),5)
        self.assertEqual(a.get_value(2, "FieldX"),4)
        self.assertEqual(a.get_value(3, "FieldX"),3)
        self.assertEqual(a.get_value(4, "FieldX"),2)
        self.assertEqual(a.get_value(5, "FieldX"),1)

    def testSetColumnCorrectNewColumnInsertsAtEndOfFields(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.set_column("FieldX",[1, 2,3,4,5,6][::-1])
        self.assertTrue("FieldX" in a.columns_ordered)
        self.assertTrue(a.columns_ordered.index("FieldX") == len(a.columns_ordered) -1)

    def testSetColumnCorrectByColumNo(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        a.set_column(0,[1, 2,3,4,5,6][::-1])
        self.assertEqual(a.get_value(0,0),6)
        self.assertEqual(a.get_value(1,0),5)
        self.assertEqual(a.get_value(2,0),4)
        self.assertEqual(a.get_value(3,0),3)
        self.assertEqual(a.get_value(4,0),2)
        self.assertEqual(a.get_value(5,0),1)

    def testSetColumnRaisesOnInExistanteColumNNumber(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
            a.set_column(5,[1, 2,3,4,5,6][::-1])
        self.assertRaises(IndexError, inner)

    def test_copy_works_on_column_names(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]},['Field1','Field3'])
        b = a.copy()
        b.drop_column("Field1")
        self.assertEqual(len(a.columns_ordered), 2)

    def test_simple_discretization(self):
        a = DataFrame({"Field1": [0,12,24,23,55,59,60,61]})
        a.digitize_column('Field1', no_of_bins=10, min=0, max=100)
        self.assertTrue((a.get_column('Field1') == [0,1,2,2,5,5,6,6]).all())

    def test_rankify(self):
        a = DataFrame({"Field1": [0,12,24,23,55,59,60,61]})
        a.rankify_column('Field1')
        self.assertTrue((a.get_column('Field1') == [0,1,3,2,4,5,6,7]).all())

    def test_rankify_reverse(self):
        a = DataFrame({"Field1": [0,12,24,23,55,59,60,61]})
        a.rankify_column('Field1', False)
        self.assertTrue((a.get_column('Field1') == [7,6,4,5,3,2,1,0]).all())

    def test_digitize_raises(self):
        a = DataFrame({"Field1": [0,12,24,23,55,59,60,61]})
        def inner():
            a.digitize_column('Field1')
        self.assertRaises(ValueError, inner)

    def test_digitize_with_bins(self):
        a = DataFrame({"Field1": [0,12,24,23,55,59,60,61]})
        a.digitize_column('Field1', bins=[50,100])
        self.assertTrue((a.get_column('Field1') == [0,0,0,0,1,1,1,1]).all())

    def test_single_rowed_dataframe_boolean_selection(self):
        a = DataFrame({"Field1": [1]})
        a[a[:,'Field1'] > 0,"Field1"] = 10
        self.assertEqual(a.get_value(0,0), 10)


class DataFrameAuxilaryTests(unittest.TestCase):
    def testConvertTo2Darray(self):
        a = DataFrame( { "Field1": [1, 2,3,4,5,6],  'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1', 'Field3'])
        b = a.as2DMatrix()
        self.assertEqual(b.shape, (6,2))
        self.assertEqual(b[0,0], 1.0)
        self.assertEqual(b[0,1], 7.0)
        self.assertEqual(b[5,1], 12.0)
        self.assertTrue(b.dtype == numpy.float64)

    def testConvertTo2DArrayRaises(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3,4,5,6], "Field2": ['def','ab','jl','ab','hgi','pqr'], 'Field3': [7.0,8.0,9.0,10.0,11.0,12.0]}, ['Field1','Field2', 'Field3'])
            b  = a.as2DMatrix()
        self.assertRaises(ValueError, inner)

class DataFrameRowNamesTests(unittest.TestCase):

    def testInitializingWithRowNames(self):
        rowNamesInOrder = ["Shu","Ha","Ri"]
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], rowNamesInOrder)
        self.assertTrue((a.row_names == numpy.array(rowNamesInOrder)).all())

    def testInitializingWithRowNamesNonUniqueRaises(self):
        def inner():
            rowNamesInOrder = ["Shu","Shu","Ri"]
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], rowNamesInOrder)
        self.assertRaises(ValueError, inner)

    def testInitializingWithRowNamesWrongNumber(self):
        def inner():
            rowNamesInOrder = ["Shu","Shu",]
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], rowNamesInOrder)
        self.assertRaises(ValueError, inner)

    def testGetRowByName(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        b = a.get_row("Ha")
        self.assertEqual(b, {"Field1": 2, "Field2": 'def', "Field3": 8.0})

    def testGetRowByNameAccessor(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        b = a["Ha","Field1"]
        self.assertEqual(b, DataFrame({"Field1": [2]}, row_names_ordered=['Ha']))

    def testGetRowByNameMixed(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        b = a[("Ha",2),"Field1"]
        self.assertEqual(b, DataFrame({"Field1": [2,3]}, row_names_ordered=["Ha","Ri"]))

    def testSetARowName(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        x = list(a.row_names)
        x[1] = "shim"
        a.row_names = x
        b = a.get_row("shim")
        self.assertEqual(b, {"Field1": 2, "Field2": 'def', "Field3": 8.0})

    def testSetARowNameRaisesOnDuplicate(self):
        def inner():
            a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
            x = list(a.row_names)
            x[1] = "Shu"
            a.row_names = x
        self.assertRaises(ValueError, inner)

    def testRowNamesRequiredForEquality(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        b = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        c = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha", "hum"])
        d = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ri","Ha"])
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)
        self.assertNotEqual(a,d)



    def testFrom2DArray(self):
        x = numpy.zeros((2,3), numpy.int32)
        x[0,0] = 1
        x[1,1] = 55
        x[1,2] = 66
        df = DataFrameFrom2dArray(x, ['One',"Two","Three"])
        self.assertEqual(df, DataFrame(
                {"One": [1,0],
                 "Two": [0, 55],
                 "Three": [0, 66]}
                , ["One", "Two","Three"]))

    def testFrom2DArrayWithRowNames(self):
        x = numpy.zeros((2,3), numpy.int32)
        x[0,0] = 1
        x[1,1] = 55
        x[1,2] = 66
        df = DataFrameFrom2dArray(x, ['One',"Two","Three"],["A","B"])
        self.assertEqual(df, DataFrame(
                {"One": [1,0],
                  "Two": [0, 55],
                 "Three": [0, 66],},
            ["One", "Two","Three"]
            , ["A","B"]))

    def testSettingIntegerRownamesRaises(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'])
        a.row_names = [ 'a','b','c']
        def inner():
            a.row_names = [55,66,77]
        self.assertEqual(a.get_value('a','Field1'), 1)
        self.assertRaises(ValueError, inner)

class LevelTests(unittest.TestCase):
  
    def test_basic_conversion(self):
        df = DataFrame({"One": ["c","a","b","b"]})
        df.turn_into_level("One")
        levs = df.get_column('One').levels
        self.assertEqual(levs[0], 'c')
        self.assertEqual(levs[1], 'a')
        self.assertEqual(levs[2], 'b')

    def testCreationFromListOneElementEach(self):
        l = ['a','b','c']
        lev = Factor(l)
        self.assertEqual(len(lev.levels),3)
        self.assertEqual(lev.levels[0],'a')
        self.assertEqual(lev.levels[1],'b')
        self.assertEqual(lev.levels[2],'c')
        self.assertEqual(lev[0],0)
        self.assertEqual(lev[1],1)
        self.assertEqual(lev[2],2)

    def testCreationFromListWithMultipleElements(self):
        l = ['a','b','c','a','b','b']
        lev = Factor(l)
        self.assertEqual(len(lev.levels),3)
        self.assertEqual(lev[0],0)
        self.assertEqual(lev[1],1)
        self.assertEqual(lev[2],2)
        self.assertEqual(lev[3],0)
        self.assertEqual(lev[4],1)
        self.assertEqual(lev[5],1)

    def testKeepsOrder(self):
        l = ['b','c','d']
        lev = Factor(l)
        self.assertEqual(len(lev.levels),3)
        self.assertEqual(lev.levels[0],'b')
        self.assertEqual(lev.levels[1],'c')
        self.assertEqual(lev.levels[2],'d')
        self.assertEqual(lev[0],0)
        self.assertEqual(lev[1],1)
        self.assertEqual(lev[2],2)

    def testWithExistingLevels(self):
        l = ['b','c','a']
        lev = Factor(l, ['a','b','c'])
        self.assertEqual(len(lev.levels),3)
        self.assertEqual(lev.levels[0],'a')
        self.assertEqual(lev.levels[1],'b')
        self.assertEqual(lev.levels[2],'c')
        self.assertEqual(lev[0],1)
        self.assertEqual(lev[1],2)
        self.assertEqual(lev[2],0)

    def testWithExistingLevelsRaisesOnTooFew(self):
        l = ['b','c','a']
        def inner():
            lev = Factor(l, ['a','c'])
        self.assertRaises(ValueError, inner)


    def testWithExistingLevelsAccepts_to_many(self):
        l = ['b','c','a']
        lev = Factor(l, ['a','b','d','c'])
        self.assertEqual(len(lev.levels),4)
        self.assertEqual(lev.levels[0],'a')
        self.assertEqual(lev.levels[1],'b')
        self.assertEqual(lev.levels[2],'d')
        self.assertEqual(lev.levels[3],'c')
        self.assertEqual(lev[0],1)
        self.assertEqual(lev[1],3)
        self.assertEqual(lev[2],0)

    def testDataframeTurnIntoLevel(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        a.turn_into_level('Field2')
        self.assertTrue(isinstance(a.get_column(1), Factor))
        levs = a.get_column(1).levels
        self.assertEqual(levs[0], 'abc')
        self.assertEqual(levs[1], 'def')
        self.assertEqual(levs[2],'hgi')
        self.assertEqual(a.get_column(1)[0], 0)
        self.assertEqual(a.get_column(1)[1], 1)
        self.assertEqual(a.get_column(1)[2], 2)
        a.turn_into_level('Field3')
        self.assertTrue(isinstance(a.get_column(2), Factor))
        levs = a.get_column(2).levels
        self.assertEqual(levs[0], 7.0)
        self.assertEqual(levs[1], 8.0)
        self.assertEqual(levs[2], 9.0)
        self.assertEqual(a.get_column(2)[0], 0)
        self.assertEqual(a.get_column(2)[1], 1)
        self.assertEqual(a.get_column(2)[2], 2)

    def testDataframeTurnIntoLevel_with_given_order(self):
        a = DataFrame( { "Field1": [1, 2,3], "Field2": ['abc','def','hgi'], 'Field3': [7.0,8.0,9.0]}, ['Field1','Field2', 'Field3'], ["Shu","Ha","Ri"])
        a.turn_into_level('Field2', ('def','hgi','abc'))
        self.assertTrue(isinstance(a.get_column(1), Factor))
        levs = a.get_column(1).levels
        self.assertEqual(levs[0], 'def')
        self.assertEqual(levs[1], 'hgi')
        self.assertEqual(levs[2],'abc')
        self.assertEqual(a.get_column(1)[0], 2)
        self.assertEqual(a.get_column(1)[1], 0)
        self.assertEqual(a.get_column(1)[2], 1)
        a.turn_into_level('Field3')
        self.assertTrue(isinstance(a.get_column(2), Factor))
        levs = a.get_column(2).levels
        self.assertEqual(levs[0], 7.0)
        self.assertEqual(levs[1], 8.0)
        self.assertEqual(levs[2], 9.0)
        self.assertEqual(a.get_column(2)[0], 0)
        self.assertEqual(a.get_column(2)[1], 1)
        self.assertEqual(a.get_column(2)[2], 2)
class DataFramePicklingTests(unittest.TestCase):

    def testSimplePickle(self):
        a = DataFrame ( {"one": [1, 2,3,4] })
        self.assertEqual(a.get_column('one').dtype, numpy.dtype('int32'))
        op = StringIO.StringIO()
        cPickle.dump(a, op)
        op.seek(0,0)
        b = cPickle.load(op)
        self.assertEqual(a, b)

    def testSimplePickleHighestProtocol(self):
        a = DataFrame ( {"one": [1, 2,3,4] })
        self.assertEqual(a.get_column('one').dtype, numpy.dtype('int32'))
        op = StringIO.StringIO()
        cPickle.dump(a, op, cPickle.HIGHEST_PROTOCOL)
        op.seek(0,0)
        b = cPickle.load(op)
        self.assertEqual(a, b)

    def testVariousDataFormats(self):
        a = DataFrame ( {"one": [1, 2,3,4], 'two': [1.0,2.0,3.0,4.0], 'three': [True, True, False, False],
                         'four': ['sha','shu','shum','shim'], 'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        op = StringIO.StringIO()
        cPickle.dump(a, op, cPickle.HIGHEST_PROTOCOL)
        op.seek(0,0)
        b = cPickle.load(op)
        self.assertEqual(a, b)

    def testEmptyPickle(self):
        a = DataFrame ( {"one": [] })
        self.assertEqual(a.get_column('one').dtype, numpy.dtype('object'))
        op = StringIO.StringIO()
        cPickle.dump(a, op)
        op.seek(0,0)
        b = cPickle.load(op)
        self.assertEqual(a, b)

    def test_mask_dumping(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,4.0], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        a.value_dict['one'].mask = False
        a.value_dict['two'].mask = True
        a.value_dict['four'].mask[2] = True
        op = StringIO.StringIO()
        cPickle.dump(a, op, cPickle.HIGHEST_PROTOCOL)
        op.seek(0,0)
        b = cPickle.load(op)
        self.assertEqual(a, b)

class DF2ExcelTests(unittest.TestCase):
    def test_read_write(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,4.0], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        nf = tempfile.NamedTemporaryFile()
        DF2Excel().write(a, nf)
        nf.seek(0,0)
        nf.flush()
        b = DF2Excel().read(nf.name)
        nf.close()
        self.assertEqual(a, b)

    def test_read_write_mixed_type(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,'SHu'], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        nf = tempfile.NamedTemporaryFile()
        DF2Excel().write(a, nf)
        nf.seek(0,0)
        nf.flush()
        b = DF2Excel().read(nf.name)
        nf.close()
        self.assertEqual(a, b)


    def test_reading_sub_columns(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,'SHu'], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        nf = tempfile.NamedTemporaryFile()
        DF2Excel().write(a, nf)
        nf.seek(0,0)
        nf.flush()
        b = DF2Excel().read(nf.name, columns_to_include=['three','four'])
        nf.close()
        self.assertEqual(a[:,('three','four')], b)

    def test_raises_on_removing_all(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,'SHu'], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        nf = tempfile.NamedTemporaryFile()
        DF2Excel().write(a, nf)
        nf.seek(0,0)
        nf.flush()
        def inner():
            b = DF2Excel().read(nf.name, columns_to_include=['nosuchcolumn'])
            nf.close()
        self.assertRaises(ValueError, inner)

    def test_raises_on_non_existant_all(self):
        a = DataFrame ( {
            "one": [1, 2,3,4], #mask = False
            'two': [1.0,2.0,3.0,'SHu'], #mask = True
            'three': [True, True, False, False], #no mask set... = False
             'four': ['sha','shu','shum','shim'], #some mask...
            'five': numpy.array([1,2,3,4], dtype=numpy.float128)})
        nf = tempfile.NamedTemporaryFile()
        DF2Excel().write(a, nf)
        nf.seek(0,0)
        nf.flush()
        def inner():
            b = DF2Excel().read(nf.name, columns_to_include=['nosuchcolumn','four'])
            nf.close()
        self.assertRaises(ValueError, inner)

def dataFrameSpeedTest():
    fn = "/k/imt/experiments/20090610_WPMY1-GW501516_BowTieAlignment/out/081208_s_7_seq_GIC-1.txt.stdout"
    fn= 'speedtest.tsv'
    import time
    start =time.time()
    df = csv2DataFrame(fn, header=True, dialect=TabDialect)
    end = time.time()
    print 'took %.2fs' % (end - start)
    print df.columns_ordered
    print df.num_rows



if __name__ == '__main__':
    import sys
    if '--speed' in sys.argv:
        dataFrameSpeedTest()
    else:
        unittest.main()
