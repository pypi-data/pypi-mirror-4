import sys

from rdflib import RDF, RDFS, URIRef, BNode, Variable, plugin
from rdflib.graph import QuotedGraph, ConjunctiveGraph

from tempfile import mkdtemp

implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")
testN3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c,?y}.
_:foo a rdfs:Class.
:a :d :c."""

from nose.tools import nottest
from nose.exc import SkipTest

#Thorough test suite for formula-aware store
@nottest # do not run on it's own - only as part of generator
def testFormulaStore(store="default", configString=None):
    try: 
        g = ConjunctiveGraph(store=store)
    except ImportError: 
        raise SkipTest("Dependencies for store '%s' not available!"%store)
  



    if configString:
        g.destroy(configString)
        g.open(configString)
    else: 
        g.open(mkdtemp(), create=True)

    g.parse(data=testN3, format="n3")
    print g.store
    try:
        for s,p,o in g.triples((None,implies,None)):
            formulaA = s
            formulaB = o

        assert type(formulaA)==QuotedGraph and type(formulaB)==QuotedGraph
        a = URIRef('http://test/a')
        b = URIRef('http://test/b')
        c = URIRef('http://test/c')
        d = URIRef('http://test/d')
        v = Variable('y')

        universe = ConjunctiveGraph(g.store)

        #test formula as terms
        assert len(list(universe.triples((formulaA,implies,formulaB))))==1

        #test variable as term and variable roundtrip
        assert len(list(formulaB.triples((None,None,v))))==1
        for s,p,o in formulaB.triples((None,d,None)):
            if o != c:
                assert isinstance(o,Variable)
                assert o == v
        s = list(universe.subjects(RDF.type, RDFS.Class))[0]
        assert isinstance(s,BNode)
        assert len(list(universe.triples((None,implies,None)))) == 1
        assert len(list(universe.triples((None,RDF.type,None)))) ==1
        assert len(list(formulaA.triples((None,RDF.type,None))))==1
        assert len(list(formulaA.triples((None,None,None))))==2
        assert len(list(formulaB.triples((None,None,None))))==2
        assert len(list(universe.triples((None,None,None))))==3
        assert len(list(formulaB.triples((None,URIRef('http://test/d'),None))))==2
        assert len(list(universe.triples((None,URIRef('http://test/d'),None))))==1

        #context tests
        #test contexts with triple argument
        assert len(list(universe.contexts((a,d,c))))==1

        #Remove test cases
        universe.remove((None,implies,None))
        assert len(list(universe.triples((None,implies,None))))==0
        assert len(list(formulaA.triples((None,None,None))))==2
        assert len(list(formulaB.triples((None,None,None))))==2

        formulaA.remove((None,b,None))
        assert len(list(formulaA.triples((None,None,None))))==1
        formulaA.remove((None,RDF.type,None))
        assert len(list(formulaA.triples((None,None,None))))==0

        universe.remove((None,RDF.type,RDFS.Class))


        #remove_context tests
        universe.remove_context(formulaB)
        assert len(list(universe.triples((None,RDF.type,None))))==0
        assert len(universe)==1
        assert len(formulaB)==0

        universe.remove((None,None,None))
        assert len(universe)==0

        g.close()
        g.store.destroy(configString)
    except:
        g.close()
        g.store.destroy(configString)
        raise


def testFormulaStores(): 
    pluginname=None
    if __name__=='__main__':
        if len(sys.argv)>1:
            pluginname=sys.argv[1]

    for s in plugin.plugins(pluginname, plugin.Store):
        if not s.getClass().formula_aware: continue

        yield testFormulaStore, s.name




if __name__ == '__main__':
    import nose
    nose.main(defaultTest=sys.argv[0])
