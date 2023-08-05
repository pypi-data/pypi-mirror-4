#!/usr/bin/python
# -*- coding: utf-8 -*-
#This file is part of pydsl.
#
#pydsl is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pydsl is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pydsl.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2012, Nestor Arocha"
__email__ = "nesaro@gmail.com"



from bnfgrammar import *
from pydsl.Grammar.Parser.RecursiveDescent import RecursiveDescentParser
from pydsl.Grammar.Parser.Weighted import WeightedParser
import unittest

class TestParsers(unittest.TestCase):
    #def testLeftRecursion(self):
    #    from pydsl.Grammar.Parser.RecursiveDescent import RecursiveDescentParser
    #    descentparser = RecursiveDescentParser(productionsetlr)
    #    result = descentparser(dots)
    #    self.assertTrue(result)

    def testRightRecursion(self):
        descentparser = RecursiveDescentParser(productionsetrr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testCenterRecursion(self):
        descentparser = RecursiveDescentParser(productionsetcr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testRecursiveDescentParserStore(self):
        descentparser = RecursiveDescentParser(productionset1)
        result = descentparser(string1)
        self.assertTrue(result)

    def testRecursiveDescentParserBad(self):
        descentparser = RecursiveDescentParser(productionset1)
        result = descentparser(string2)
        self.assertFalse(result)

    def testRecursiveDescentParserNull(self):
        descentparser = RecursiveDescentParser(productionset2)
        result = descentparser(string3)
        self.assertTrue(result)

    def testRecursiveDescentParserNullBad(self):
        descentparser = RecursiveDescentParser(productionset2)
        result = descentparser(string4)
        self.assertFalse(result)

    @unittest.skip
    def testLR0ParserStore(self):
        from pydsl.Grammar.Parser.LR0 import LR0Parser
        parser = LR0Parser(productionset1)
        result = parser(string1)
        self.assertTrue(result)

    @unittest.skip
    def testLR0ParserBad(self):
        from pydsl.Grammar.Parser.LR0 import LR0Parser
        parser = LR0Parser(productionset1)
        result = parser(string2)
        self.assertFalse(result)

    @unittest.skip
    def testWeightedRightRecursion(self):
        parser = WeightedParser(productionsetrr)
        result = parser(dots)
        self.assertTrue(result)

    @unittest.skip
    def testWeightedCenterRecursion(self):
        descentparser = RecursiveDescentParser(productionsetcr)
        result = descentparser(dots)
        self.assertTrue(result)

    @unittest.skip
    def testWeightedParserStore(self):
        parser = WeightedParser(productionset1)
        result = parser(string1)
        self.assertTrue(result)

    @unittest.skip
    def testWeightedParserBad(self):
        parser = WeightedParser(productionset1)
        result = parser(string2)
        self.assertFalse(result)

    @unittest.skip
    def testWeightedParserNull(self):
        parser = WeightedParser(productionset2)
        result = parser(string3)
        self.assertTrue(result)

    @unittest.skip
    def testWeightedParserNullBad(self):
        parser = WeightedParser(productionset2)
        result = parser(string4)
        self.assertFalse(result)

class TestWeightedParser(unittest.TestCase):
    @unittest.skip
    def testLeftRecursion(self):
        parser = WeightedParser(productionsetlr)
        result = parser(dots)
        self.assertTrue(result)

    @unittest.skip
    def testMixResults(self):
        from pydsl.Grammar.Parser.Parser import mix_results
        from pydsl.Grammar.Tree import ParseTree
        from pydsl.Grammar.Symbol import NullSymbol
        result1 = ParseTree(0, 3, [NullSymbol()], "", None)
        result2 = ParseTree(0, 5, [NullSymbol()], "", None)
        result3 = ParseTree(3, 6, [NullSymbol()], "", None)
        result4 = ParseTree(6, 8, [NullSymbol()], "", None)
        result5 = ParseTree(7, 8, [NullSymbol()], "", None)
        set1 = [result1, result2]
        set1b = [set1]
        set2 = [result3]
        set2b = [set2]
        set3 = [result4, result5]
        set3b = [set3]
        result = mix_results([set1b, set2b, set3b], None)
        #TODO: check result
        self.assertTrue(len(result) == 1)

