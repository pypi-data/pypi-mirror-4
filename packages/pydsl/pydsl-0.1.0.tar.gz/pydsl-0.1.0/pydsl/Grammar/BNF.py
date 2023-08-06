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

"""Production rules"""

from pydsl.Grammar.Symbol import Symbol, TerminalSymbol, NullSymbol, EndSymbol
from pydsl.Grammar.Definition import GrammarDefinition

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"


class Production(object):
    def __init__(self, leftside, rightside):
        #Left side must have at least one non terminal symbol
        for element in rightside:
            if not isinstance(element, Symbol):
                raise TypeError
        self.leftside = leftside
        self.rightside = rightside

    def __str__(self):
        """Pretty print"""
        leftstr = " ".join([ x.name for x in self.leftside])
        rightstr = " ".join([ str(x) for x in self.rightside])
        return leftstr + "::=" + rightstr

    def __eq__(self, other):
        try:
            if len(self.leftside) != len(other.leftside):
                return False
            if len(self.rightside) != len(other.rightside):
                return False
            for index in range(len(self.leftside)):
                if self.leftside[index] != other.leftside[index]:
                    return False
            for index in range(len(self.rightside)):
                if self.rightside[index] != other.rightside[index]:
                    return False
        except AttributeError:
            return False
        return True

    @property
    def name(self):
        if len(self.leftside) != 1:
            raise Exception
        return self.leftside[0].name


class BNFGrammar(GrammarDefinition): #Only stores a ruleset, and methods to ask properties or validity check 
    def __init__(self, initialsymbol, fulllist, options=None):
        self._initialsymbol = initialsymbol
        for rule in fulllist:
            if fulllist.count(rule) >1:
                raise ValueError("Duplicated rule: " + str(rule))
        self.fulllist = fulllist
        if not options: options = {}
        self.options = options

    def alphabet(self):
        from pydsl.Alphabet.Definition import AlphabetListDefinition
        return AlphabetListDefinition([x.gd for x in self.terminalsymbollist])

    @property
    def productionlist(self):
        return [x for x in self.fulllist if isinstance(x, Production)]

    @property
    def terminalsymbollist(self):
        return [x for x in self.fulllist if isinstance(x, TerminalSymbol)]

    @property
    def symbollist(self):
        result = []
        for x in self.productionlist:
            for y in x.leftside + x.rightside:
                if y not in result:
                    result.append(y)
        return result

    @property
    def first(self):
        """Returns the list of terminalsymbols that can be the first element of this grammar"""
        return [x.first for x in self.terminalsymbollist]

    def first_lookup(self, symbol):
        """Returns the first TerminalSymbols produced by the input symbol within this grammar definition"""
        if isinstance(symbol, (TerminalSymbol, NullSymbol)):
            return [symbol]
        result = []
        for x in self.productionlist:
            if x.leftside[0] != symbol:
                continue
            for y in x.rightside:
                current_symbol_first = self.first_lookup(y)
                result += current_symbol_first
                if NullSymbol not in current_symbol_first:
                    break # This element doesn't have Null in its first set so there is no need to continue
        if not result:
            raise KeyError("Symbol doesn't exist in this grammar")
        return result

    def next_lookup(self, symbol):
        """Returns the next TerminalSymbols produced by the input symbol within this grammar definition"""
        result = []
        if symbol == self.initialsymbol:
            result.append(EndSymbol())
        for production in self.productionlist:
            if symbol in production.rightside:
                nextindex = production.rightside.index(symbol)+1
                while nextindex < len(production.rightside):
                    nextsymbol = production.rightside[nextindex]
                    firstlist = self.first_lookup(nextsymbol)
                    cleanfirstlist = [x for x in firstlist if x != NullSymbol()]
                    result.append(cleanfirstlist)
                    if NullSymbol() not in firstlist:
                        break
                else:
                    result += self.next_lookup(production.leftside[0]) #reached the end of the rightside

        return result

    @property
    def left_recursive(self):# -> bool:
        """Tests if exists left recursion"""
        #TODO
        raise NotImplementedError

    @property
    def right_recursive(self):# -> bool:
        """Tests if exists right recursion"""
        #TODO
        raise NotImplementedError

    @property
    def is_abstract(self):
        """Returns true if the grammar contains an unknown symbol"""
        from pydsl.Grammar.Symbol import UnknownSymbol
        return UnknownSymbol in self.fulllist

    def __eq__(self, other):
        if not isinstance(other,BNFGrammar):
            return False
        if self._initialsymbol != other.initialsymbol:
            return False
        for index in range(len(self.productionlist)):
            if self.productionlist[index] != other.productionlist[index]:
                return False
        return True

    #def __getitem__(self, index):
    #    for rule in self.productionlist:
    #        if rule.name == index:
    #            return rule
    #    raise IndexError

    @property
    def initialsymbol(self):
        return self._initialsymbol

    @property
    def main_production(self):
        """Returns main rule"""
        for rule in self.productionlist:
            if rule.leftside[0] == self._initialsymbol:
                return rule
        raise IndexError

    def getProductionsBySide(self, symbollist, side = "left"):
        result = []
        for rule in self.productionlist: #FIXME Is iterating over production only
            part = None
            if side == "left":
                part = rule.leftside
            elif side == "right":
                part = rule.rightside
            else:
                raise KeyError
            valid = True
            if len(part) != len(symbollist):
                valid = False
            for ruleindex in range(len(part)):
                if part[ruleindex] != symbollist[ruleindex]:
                    valid = False
                    break
            if valid:
                result.append(rule)
        if not result:
            raise IndexError("Symbol: %s" % str([str(x) for x in symbollist]))

        return result

    def getProductionByBothSides(self, leftsymbollist, rightsymbollist):
        for rule in self.productionlist:
            valid = True
            if len(rule.leftside) != len(leftsymbollist):
                continue
            if len(rule.rightside) != len(rightsymbollist):
                continue
            for ruleindex in range(len(rule.leftside)):
                if leftsymbollist[ruleindex] != rule.leftside[ruleindex]:
                    valid = False
                    break
            if not valid:
                continue
            for ruleindex in range(len(rule.rightside)):
                if rightsymbollist[ruleindex] != rule.rightside[ruleindex]:
                    valid = False
                    break
            if not valid:
                continue
            if valid:
                return rule
        raise IndexError

    def getSymbols(self):
        """Returns every symbol"""
        symbollist = []
        for rule in self.productionlist:
            for symbol in rule.leftside + rule.rightside:
                if symbol not in symbollist:
                    symbollist.append(symbol)
        symbollist += self.terminalsymbollist
        return symbollist

    def getProductions(self):
        return self.productionlist

    def getProductionIndex(self, rule):
        return self.productionlist.index(rule)

    def __str__(self):
        return str(list(map(str,self.productionlist)))
