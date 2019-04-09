import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 pyspark-shell py2neo'

from pip._internal import main as pipmain 
pipmain(['install','py2neo'])


from py2neo import Database
from py2neo import Graph, Node, Relationship, Path, NodeMatcher, RelationshipMatcher
import json

def connectGraph():
    userName =  "neo4j"
    userPass = "password"

    # db = Database(dbString)
    graphdb = Graph(scheme="bolt", host="neo4j", port=7687, secure=True, auth=(userName, userPass))
    return graphdb


def _createPublisher(id, title, year, lang, citation, url ):
        graph = connectGraph()
        print("Creating Publisher id:"+ id + " title:" + title)
        #pub = Node('Paper','AMINER',name=name, title=title, year=year, lang=lang)
        matcher = NodeMatcher(graph)
        pbNode = matcher.match("Paper", id=id).first()
        if pbNode == None:
            pbNode = Node('Paper',name=title, id=id, year=year, lang=lang, citation=citation, url=str(url))
            #pbNode.labels.add(title)
            graph.create(pbNode)
        else:
            print('update:' + str(citation))
            pbNode['name'] = title
            pbNode['year'] = year
            pbNode['lang'] = lang
            pbNode['citation'] = citation
            pbNode['url'] = str(url)    

            graph.merge(pbNode)
            graph.push(pbNode)
        #graph.create(bradley,matthew,lisa,john,annie,ripley)
                
        # print("Publish Created")
        #Create a Dictionary and return back the nodes for further operations
        #people = {'bradley':bradley,'matthew':matthew,'lisa':lisa,'john':john,'annie':annie,'ripley':ripley}
        return pbNode

def _createAuthor(pub, names):
    graph = connectGraph()
    print('   Creating Authors')
    for auth in names:
        matcher = NodeMatcher(graph)
        aNode = matcher.match("Author", name=auth['name']).first()
        try:
            org = auth['org']
        except KeyError:
            org = ''
        if aNode is None:
            if org == '':
                aNode = Node('Author', name=auth['name'])
            else:
                aNode = Node('Author', name=auth['name'], org=org)
            path_1 = Path(aNode, 'AUTHORED', pub)
            graph.create(path_1)
        else:
            #Check the relationship
            rmatcher = RelationshipMatcher(graph)
            auNode = rmatcher.match((aNode,pub), "AUTHORED").first()
            if auNode is None:
                path_1 = Path(aNode, 'AUTHORED', pub)
                graph.create(path_1)

def _createReferences(pub, references):
    graph = connectGraph()
    print('   Creating References')
    for ref in references:
        #Find the Paper details
        matcher = NodeMatcher(graph)
        pbNode = matcher.match("Paper", id=ref).first()
        if pbNode == None:
            #path_1 = Node('PAPER', 'AMINER', name=ref)
            pbNode = Node('Paper', id=ref)
            path_1 = Path(pub, 'REFERENCE', pbNode)
            graph.create(path_1)
        else:
            #Check for existing relationship
            rmatcher = RelationshipMatcher(graph)
            auNode = rmatcher.match((pbNode,pub), "REFERENCE").first()
            if auNode is None:
                path_1 = Path(pub, 'REFERENCE', pbNode)
                graph.create(path_1)
       
def _createKeywords(pub, keywords):
    graph = connectGraph()
    print('   Creating Keywords')
    for kw in keywords:
        #Find keywords  TODO : Check for duplicate on re-run
        matcher = NodeMatcher(graph)
        #pbNode = matcher.match("KEYWORDS", kw.upper(), name=kw.lower()).first()
        pbNode = matcher.match("Keywords", kw.lower(), name=kw.lower()).first()
        if pbNode == None:
            pbNode = Node('Keywords', kw.lower(), name=kw.lower())
            path_1 = Path(pub, 'CONTAINS', pbNode)
            graph.create(path_1)
        else:
            #Check for existing relationship
            rmatcher = RelationshipMatcher(graph)
            auNode = rmatcher.match((pbNode,pub), "CONTAINS").first()
            if auNode is None:
                path_1 = Path(pub, 'CONTAINS', pbNode)
                graph.create(path_1)
         


def formatNodes(message1):
        # Parse json string to Publisher, authors, References
        #message = message1.toDF()
        print("**** Inside formatNodes")
        print(type(message1))
        print(message1)
        message = json.dumps(message1)
        print(type(message))
        
        #message.pprint()
        #for i in message.collect():
        #    print(i)
        #    i.pprint()

        jsonData = json.loads(message)
        
        id1 = jsonData['id']
        title = jsonData['title']
        
        try:
            year = jsonData['year']
        except KeyError:
            year = 0000
            
        #year = jsonData['year']
        try:
            lang = jsonData['lang']
        except KeyError:
            lang = 'missing'
            
        #lang = jsonData['lang']
        try:
            citation = jsonData['n_citation']
        except KeyError:
            citation = 0

        try:
            url = jsonData['url']
        except KeyError:
            url = ''
        print(url)

        pub = _createPublisher(id1, title, year, lang, citation, url)
        
        if jsonData.get('authors') is not None:
            _createAuthor(pub, jsonData['authors'])

        if jsonData.get('references') is not None:
            _createReferences(pub, jsonData['references'])
        
        if jsonData.get('keywords') is not None:
            _createKeywords(pub, jsonData['keywords'])
        #print(message)


def getAuthorPublications(name, top):
    print('Getting Author Publications')
    graph = connectGraph()
    # WHERE a.name = {name}
    query = '''
        MATCH (a:Author { name={name})-[r:AUTHORED]->(p:Paper)
        RETURN p, a
        ORDER BY p.year DESC LIMIT {top}
        '''
    res = graph.run(query, name=name, top=top)
    print(res)

    return res


def getAuthorPopularPublications(name, top):
    print('Getting Author Popular Publications')
    graph = connectGraph()
    query = '''
        MATCH (a:Author { name={name})-[r:AUTHORED]->(p:Paper)
        RETURN p, a
        ORDER BY p.year,p.citation DESC LIMIT {top}
        '''
    res = graph.run(query, name=name, top=top)
    print(res)

    return res

def getPopularPublicationsByCitation(top):
    print('Getting Popular(citated) Publications')
    graph = connectGraph()
    query = '''
        MATCH p=(Paper)-[r:AUTHORED]->(m)
        RETURN DISTINCT(m)
        ORDER BY m.citation DESC, m.year DESC LIMIT {top}
        '''
    res = graph.run(query, top=top)
    print(res)

    return res

# returns the Popular Publication referenced in other Publications
def getPopularPublicationsByReferences(top):
    print('Getting Popular(references) Publications')
    graph = connectGraph()
    query = '''
        MATCH p=(Paper)-[r:REFERENCE]->(m) 
        RETURN m,COUNT(m) ORDER BY COUNT(m) DESC LIMIT {top}
        '''
    res = graph.run(query, top=top)
    print(res)

    return res
 
 # TOP Authored Paper
 # MATCH p=(Paper)-[r:AUTHORED]->(m) RETURN m,r,COUNT(m) ORDER BY COUNT(m) DESC LIMIT 25


def getPublicationsByKeywords(keyword, top):
    graph = connectGraph()
    query = '''
        MATCH (p:PAPER)<-[:CONTAINS]-(k:Keyword)
        WHERE k.word = {keyword}
        RETURN p, k
        ORDER BY p.year,p.citation DESC LIMIT {top}
        '''
    res = graph.run(query, keyword=keyword, top=top)
    return res

# Scenario
# 1 - Latest papers by author
# 2 - latest papers by topic