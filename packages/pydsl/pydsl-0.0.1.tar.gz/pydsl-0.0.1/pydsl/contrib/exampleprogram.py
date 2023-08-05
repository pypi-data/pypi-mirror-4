from pydsl.Config import VERSION, GLOBALCONFIG
from pydsl.Memory.Search.Searcher import MemorySearcher
from pydsl.Memory.Search.Indexer import Indexer
from pydsl.Memory.Loader import load_function
from pydsl.Guess import Guesser

mystring = "True||False"
guesser = Guesser()
grammarlist = guesser(mystring)
print(grammarlist)
assert("LogicalExpression" in grammarlist)
searcher = MemorySearcher([Indexer(x) for x in GLOBALCONFIG.memorylist])
availabletransformers = [x['identifier'] for x in searcher.search({'inputlist':{'$in':'LogicalExpression'}})] 
print(availabletransformers)
solver = load_function('logicalSolver')
result = solver({'input':mystring})
print(result)
