from py2neo import Database
from py2neo import Graph, Node, Relationship, Path, NodeMatcher, RelationshipMatcher
import json


class PrepareGraphNodes(object):

    # graph = None

    def __init__(self, bolt, uri, user, password):
        print("Init...")
        #dbString = "bolt://localhost:7687"
        #userName =  "user1"
        #userPass = "user1"

        self.graph = Graph(scheme="bolt", host="localhost", port=7687, secure=True, auth=(user, password))
        #with open("stopwords.txt", 'rb+') as f:
        #    stopWords = f.read().split('\n')
            
#class Record:

     
#    def __init__(self, string):

#        return string


def connectGraph():
    userName =  "user1"
    userPass = "user1"

    # db = Database(dbString)
    graphdb = Graph(scheme="bolt", host="localhost", port=7687, secure=True, auth=(userName, userPass))
    return graphdb


def _createPublisher(id, title, year, lang, citation, url ):
        graph = connectGraph()
        print("Creating Publisher id:"+ id + " title:" + title)
        #pub = Node('Paper','AMINER',name=name, title=title, year=year, lang=lang)
        matcher = NodeMatcher(graph)
        pbNode = matcher.match("Paper", id=id).first()
        if pbNode == None:
            pbNode = Node('Paper',name=title, id=id, year=year, lang=lang, citation=citation, url=str(url))
            graph.create(pbNode)
        else:
            print('update' + str(citation))
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
        if aNode is None:
            aNode = Node('Author', name=auth['name'])
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
         


def formatNodes(message):
        # Parse json string to Publisher, authors, References
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

# x = PrepareGraphNodes("bolt","localhost",7687, "user1", "user1")
# x.createPublisher('{"id": "53e99837b7602d970205d318", "title": "Planet 1894 AX", "authors": [{"name": "Gustav Witt"}], "venue": "Astronomische Nachrichten", "year": 1894, "page_start": "183", "page_end": "184", "lang": "en", "volume": "135", "issue": "10", "doi": "10.1002/asna.18941351008", "url": ["http://dx.doi.org/10.1002/asna.18941351008"]}')
#x.print_greeting('{"id": "53e99837b7602d970205d319", "title": "Planet (132) Aethra", "authors": [{"name": "Wilhelm Luther"}], "venue": "Astronomische Nachrichten", "year": 1894, "page_start": "207", "page_end": "208", "lang": "en", "volume": "136", "issue": "13", "doi": "10.1002/asna.18941361313", "url": ["http://dx.doi.org/10.1002/asna.18941361313"]}')
#x.print_greeting('{"id": "53e99837b7602d970205d31a", "title": "Planet (113) Amalthea", "authors": [{"name": "O. Knopf"}], "venue": "Astronomische Nachrichten", "year": 1897, "page_start": "215", "page_end": "216", "lang": "en", "volume": "143", "issue": "12-13", "doi": "10.1002/asna.18971431206", "url": ["http://dx.doi.org/10.1002/asna.18971431206"]}')



#formatNodes('{"id": "53e99837b7602d970205d318", "title": "Planet 1894 AX", "authors": [{"name": "Gustav Witt"}], "venue": "Astronomische Nachrichten", "year": 1894, "page_start": "183", "page_end": "184", "lang": "en", "volume": "135", "issue": "10", "doi": "10.1002/asna.18941351008", "url": ["http://dx.doi.org/10.1002/asna.18941351008"]}')
#formatNodes('{"id": "53e99837b7602d970205d319", "title": "Planet (132) Aethra", "authors": [{"name": "Wilhelm Luther"}], "venue": "Astronomische Nachrichten", "year": 1894, "page_start": "207", "page_end": "208", "lang": "en", "volume": "136", "issue": "13", "doi": "10.1002/asna.18941361313", "url": ["http://dx.doi.org/10.1002/asna.18941361313"], "references":["53e99837b7602d970205d318"]}')
#formatNodes('{"id": "53e99837b7602d970205d31a", "title": "Planet (113) Amalthea", "authors": [{"name": "O. Knopf"}], "venue": "Astronomische Nachrichten", "year": 1897, "page_start": "215", "page_end": "216", "lang": "en", "volume": "143", "issue": "12-13", "doi": "10.1002/asna.18971431206", "url": ["http://dx.doi.org/10.1002/asna.18971431206"]}')
#formatNodes('{"id": "53e99837b7602d970205d324", "title": "Network-Oblivious Algorithms.", "authors": [{"name": "Gianfranco Bilardi"}, {"name": "Andrea Pietracaprina"}, {"name": "Geppino Pucci"}, {"name": "Michele Scquizzato"}, {"name": "Francesco Silvestri"}], "venue": "international parallel and distributed processing symposium", "year": 2007, "keywords": ["any machines", "are nevertheless ecient", "computational modeling", "space technology", "computer networks", "computational complexity", "parallel algorithms", "concurrent computing", "model of computation", "bandwidth", "parallel processing", "algorithm design and analysis"], "n_citation": 21, "page_start": "1", "page_end": "10", "lang": "en", "volume": "abs/1404.3318", "doi": "10.1109/IPDPS.2007.370243", "url": ["http://dx.doi.org/10.1109/IPDPS.2007.370243", "http://arxiv.org/abs/1404.3318"], "references": ["53e9b110b7602d9703b9057d", "53e9b71db7602d97042b5023", "53e9ac4eb7602d970362122d", "53e99809b7602d970201cb83", "53e999ffb7602d970224a87d", "56d8fed2dabfae2eeec9f99e", "53e9b70fb7602d97042a59fe", "53e9ab4fb7602d97034e0e96", "53e9a540b7602d9702e65cd0", "53e9aadfb7602d97034623d0", "53e9ab3db7602d97034caffd", "53e9a855b7602d970319d0c2", "53e9ac75b7602d9703648e12", "53e9bbc2b7602d970481144f", "53e999ffb7602d970224dbf8", "53e9bc10b7602d97048758c9", "53e9b797b7602d9704340043", "53e9ab69b7602d9703505fec", "53e9a8ffb7602d970324d8f5", "53e9a246b7602d9702b4bd96", "53e9b923b7602d970450ffba", "53e9aadfb7602d9703461d05", "53e999fab7602d9702243d88", "53e9b74bb7602d97042ea295", "53e999ffb7602d970224dbf9", "56d8141bdabfae2eee65e9a5", "53e99837b7602d970205d324", "53e9a9ebb7602d970334dd36", "53e9af99b7602d97039e3edc", "53e9b976b7602d970456398f", "53e99f4fb7602d9702820cb7", "53e9a0adb7602d97029959f4", "53e99960b7602d97021a3a5e","53e99837b7602d970205d31a"]}')

#formatNodes('{"id": "53e99837b7602d970205d31a", "title": "Planet (113) Amalthea", "authors": [{"name": "O. Knopf"}], "venue": "Astronomische Nachrichten", "year": 1897, "page_start": "215", "page_end": "216", "lang": "en", "volume": "143", "issue": "12-13", "doi": "10.1002/asna.18971431206", "url": ["http://dx.doi.org/10.1002/asna.18971431206"]}')
#formatNodes('{"id": "53e99837b7602d970205d31b", "title": "Planet (113) Amalthea", "authors": [{"name": "F. Ristenpart"}], "venue": "Astronomische Nachrichten", "year": 1902, "page_start": "13", "page_end": "14", "lang": "en", "volume": "159", "issue": "1", "doi": "10.1002/asna.19021590109", "url": ["http://dx.doi.org/10.1002/asna.19021590109"]}')
#formatNodes('{"id": "53e99837b7602d970205d31c", "title": "Planet 1907 AL", "authors": [{"name": "Fritz Cohn"}], "venue": "Astronomische Nachrichten", "year": 1914, "page_start": "331", "page_end": "332", "lang": "en", "volume": "199", "issue": "22", "doi": "10.1002/asna.19141992203", "url": ["http://dx.doi.org/10.1002/asna.19141992203"]}')
#formatNodes('{"id": "53e99837b7602d970205d31d", "title": "Plan\u00e8te 1927 AA.", "authors": [{"name": "J. Comas Sol\u00e1"}], "venue": "Astronomische Nachrichten", "year": 1927, "page_start": "327", "page_end": "328", "lang": "en", "volume": "230", "issue": "17", "doi": "10.1002/asna.19272301705", "url": ["http://dx.doi.org/10.1002/asna.19272301705"]}')
#formatNodes('{"id": "53e99837b7602d970205d31e", "title": "Plan\u00e8te 113 Amalthea", "authors": [{"name": "E. de la Villemarqu\u00e9"}], "venue": "Astronomische Nachrichten", "year": 1930, "page_start": "265", "page_end": "266", "lang": "en", "volume": "238", "issue": "16", "doi": "10.1002/asna.19302381606", "url": ["http://dx.doi.org/10.1002/asna.19302381606"]}')
#formatNodes('{"id": "53e99837b7602d970205d31f", "title": "Post-1984 America", "authors": [{"name": "Lee Rainwater"}], "venue": "Society", "year": 1972, "page_start": "18", "page_end": "27", "lang": "en", "volume": "9", "issue": "4", "doi": "10.1007/BF02695911", "url": ["http://dx.doi.org/10.1007/BF02695911"]}')
#formatNodes('{"id": "53e99837b7602d970205d321", "title": "Piaget: 100 anos", "authors": [{"name": "Luci Banks-Leite"}], "year": 1998, "lang": "en", "volume": "19", "issue": "63", "doi": "10.1590/S0101-73301998000200011", "url": ["http://dx.doi.org/10.1590/S0101-73301998000200011"]}')
#formatNodes('{"id": "53e99837b7602d970205d322", "title": "Notes on approximation", "authors": [{"name": "G. G. Lorentz"}], "venue": "Journal of Approximation Theory", "year": 1989, "page_start": "360", "page_end": "365", "lang": "en", "volume": "56", "issue": "3", "doi": "10.1016/0021-9045(89)90125-1", "url": ["http://dx.doi.org/10.1016/0021-9045(89)90125-1"], "references": ["53e99b56b7602d97023fd8cd"]}')
#formatNodes('{"id": "53e99837b7602d970205d323", "title": "Note of amplification", "authors": [{"name": "Robert W. Floyd", "org": "Stanford Univ., Stanford, CA"}], "venue": "Commun. ACM", "year": 1960, "page_start": "346", "page_end": "346", "lang": "en", "volume": "3", "issue": "6", "doi": "10.1145/367297.367314", "url": ["http://dx.doi.org/10.1145/367297.367314", "http://doi.acm.org/10.1145/367297.367314"]}')
#formatNodes('{"id": "53e99837b7602d970205d324", "title": "Network-Oblivious Algorithms.", "authors": [{"name": "Gianfranco Bilardi"}, {"name": "Andrea Pietracaprina"}, {"name": "Geppino Pucci"}, {"name": "Michele Scquizzato"}, {"name": "Francesco Silvestri"}], "venue": "international parallel and distributed processing symposium", "year": 2007, "keywords": ["any machines", "are nevertheless ecient", "computational modeling", "space technology", "computer networks", "computational complexity", "parallel algorithms", "concurrent computing", "model of computation", "bandwidth", "parallel processing", "algorithm design and analysis"], "n_citation": 21, "page_start": "1", "page_end": "10", "lang": "en", "volume": "abs/1404.3318", "doi": "10.1109/IPDPS.2007.370243", "url": ["http://dx.doi.org/10.1109/IPDPS.2007.370243", "http://arxiv.org/abs/1404.3318"], "abstract": "The design of algorithms that can run unchanged yet efficiently on a variety of machines characterized by different degrees of parallelism and communication capabilities is a highly desirable goal. We propose a framework for network-obliviousness based on a model of computation where the only parameter is the prob- lem''s input size. Algorithms are then evaluated on a model with two parameters, capturing parallelism and granularity of communication. We show that, for a wide class of network-oblivious algorithms, optimality in the latter model implies optimality in a block-variant of the Decomposable BSP model, which effectively de- scribes a wide and significant class of parallel plat- forms. We illustrate our framework by providing op- timal network-oblivious algorithms for a few key prob- lems, and also establish some negative results.", "references": ["53e9b110b7602d9703b9057d", "53e9b71db7602d97042b5023", "53e9ac4eb7602d970362122d", "53e99809b7602d970201cb83", "53e999ffb7602d970224a87d", "56d8fed2dabfae2eeec9f99e", "53e9b70fb7602d97042a59fe", "53e9ab4fb7602d97034e0e96", "53e9a540b7602d9702e65cd0", "53e9aadfb7602d97034623d0", "53e9ab3db7602d97034caffd", "53e9a855b7602d970319d0c2", "53e9ac75b7602d9703648e12", "53e9bbc2b7602d970481144f", "53e999ffb7602d970224dbf8", "53e9bc10b7602d97048758c9", "53e9b797b7602d9704340043", "53e9ab69b7602d9703505fec", "53e9a8ffb7602d970324d8f5", "53e9a246b7602d9702b4bd96", "53e9b923b7602d970450ffba", "53e9aadfb7602d9703461d05", "53e999fab7602d9702243d88", "53e9b74bb7602d97042ea295", "53e999ffb7602d970224dbf9", "56d8141bdabfae2eee65e9a5", "53e99837b7602d970205d324", "53e9a9ebb7602d970334dd36", "53e9af99b7602d97039e3edc", "53e9b976b7602d970456398f", "53e99f4fb7602d9702820cb7", "53e9a0adb7602d97029959f4", "53e99960b7602d97021a3a5e"]}')
#formatNodes('{"id": "53e99837b7602d970205d325", "title": "Neurobiology of addiction", "authors": [{"name": "Aviel Goodman"}], "venue": "Biochemical Pharmacology", "year": 2008, "keywords": ["gambling", "neurobiology", "bulimia", "neuroscience", "addiction", "substance abuse", "substance use disorder"], "page_start": "266", "page_end": "322", "lang": "en", "volume": "75", "issue": "1", "issn": "Biochemical Pharmacology", "doi": "10.1016/j.bcp.2007.07.030", "url": ["http://dx.doi.org/10.1016/j.bcp.2007.07.030"], "abstract": "Evidence that psychoactive substance use disorders, bulimia nervosa, pathological gambling, and sexual addiction share an underlying biopsychological process is summarized. Definitions are offered for addiction and addictive process , the latter being the proposed designation for the underlying biopsychological process that addictive disorders are hypothesized to share. The addictive process is introduced as an interaction of impairments in three functional systems: motivation-reward, affect regulation, and behavioral inhibition. An integrative review of the literature that addresses the neurobiology of addiction is then presented, organized according to the three functional systems that constitute the addictive process. The review is directed toward identifying candidate neurochemical substrates for the impairments in motivation-reward, affect regulation, and behavioral inhibition that could contribute to an addictive process.", "references": ["53e9aeebb7602d970391b4d4", "55a40b3e612ca648688289e9"]}')
#formatNodes('{"id": "53e99837b7602d970205d326", "title": "Neurobiology of arachnids", "authors": [{"name": "Thomas C. Cheng", "org": "Marine Biomedical Research Program Medical University of South Carolina Charleston, South Carolina 29412 USA"}], "venue": "Journal of Invertebrate Pathology", "year": 1986, "page_start": "388", "page_end": "388", "lang": "en", "volume": "48", "issue": "3", "issn": "Journal of Invertebrate Pathology", "doi": "10.1016/0022-2011(86)90071-6", "url": ["http://dx.doi.org/10.1016/0022-2011(86)90071-6"]}')
#formatNodes('{"id": "53e99837b7602d970205d327", "title": "Neuroanatomy of autism", "authors": [{"name": "David G. Amaral", "org": "The M.I.N.D. Institute, Department of Psychiatry and Behavioral Sciences, University of California, Davis, 2825 50th Street, Sacramento, CA 95817, USA"}, {"name": "Cynthia Mills Schumann", "org": "Department of Neurosciences, University of California, San Diego, 8110 La Jolla Shores Drive, Suite 201, La Jolla, CA 92037, USA"}, {"name": "Christine Wu Nordahl", "org": "The M.I.N.D. Institute, Department of Psychiatry and Behavioral Sciences, University of California, Davis, 2825 50th Street, Sacramento, CA 95817, USA"}], "venue": "Trends in Neurosciences", "year": 2008, "n_citation": 1022, "page_start": "137", "page_end": "145", "lang": "en", "volume": "31", "issue": "3", "issn": "Trends in Neurosciences", "doi": "10.1016/j.tins.2007.12.005", "url": ["http://dx.doi.org/10.1016/j.tins.2007.12.005"], "abstract": "Autism spectrum disorder is a heterogeneous, behaviorally defined, neurodevelopmental disorder that occurs in 1 in 150 children. Individuals with autism have deficits in social interaction and verbal and nonverbal communication and have restricted or stereotyped patterns of behavior. They might also have co-morbid disorders including intellectual impairment, seizures and anxiety. Postmortem and structural magnetic resonance imaging studies have highlighted the frontal lobes, amygdala and cerebellum as pathological in autism. However, there is no clear and consistent pathology that has emerged for autism. Moreover, recent studies emphasize that the time course of brain development rather than the final product is most disturbed in autism. We suggest that the heterogeneity of both the core and co-morbid features predicts a heterogeneous pattern of neuropathology in autism. Defined phenotypes in larger samples of children and well-characterized brain tissue will be necessary for clarification of the neuroanatomy of autism.", "references": ["53e9aa61b7602d97033d129c", "53e9ba38b7602d970464682f", "55a4d6ef612c6b12aafb68a0", "53e9bda6b7602d9704a52675", "53e9b22eb7602d9703cc8b27", "53e9b856b7602d970441915f", "53e9a1dbb7602d9702ad57c4", "53e9ac70b7602d9703643363", "53e9b6b8b7602d970423daa0", "53e9983db7602d9702069455", "53e9b550b7602d970408a26e", "53e9b1d7b7602d9703c6a9bf", "53e9b57cb7602d97040b8bb9", "53e9b1cab7602d9703c5e3ea", "53e9ac95b7602d97036713e7", "55a4af76612ca64868a0109f", "53e9b9c7b7602d97045be2a8", "53e9b4bab7602d9703fd3128", "53e99e7fb7602d97027466da", "53e9b9b4b7602d97045a8d03", "53e99a62b7602d97022cfe6b", "53e9af87b7602d97039cbc0a", "53e9ac3db7602d97036094f6", "53e9a357b7602d9702c623f9", "53e9b2d6b7602d9703d84cf3", "53e99866b7602d970209dcf2", "53e9b05cb7602d9703abd5ea", "53e9b895b7602d9704468c27", "53e99fd6b7602d97028b3108", "53e99fbcb7602d97028923b0", "53e9a8b1b7602d9703201a6e", "53e9ac21b7602d97035e4015", "53e99d58b7602d9702610425", "53e9a0e0b7602d97029ccc34", "53e9ab00b7602d9703483318", "53e99960b7602d97021a36af", "53e9aa56b7602d97033c430b", "53e99bd5b7602d9702481939", "53e9b489b7602d9703f92af0", "53e9bc2cb7602d9704896798", "53e9ac95b7602d970366d079", "56d90238dabfae2eeedf04ce", "53e9b930b7602d9704519057", "53e9ad7cb7602d9703770842", "53e9a2b2b7602d9702bb9769", "53e99c84b7602d9702535b02", "53e9acf0b7602d97036d0de9", "53e9b3b7b7602d9703e9a8f6", "53e9a1a1b7602d9702a9573a", "53e99e38b7602d97026fcdcd", "53e9b1d1b7602d9703c634f7", "53e9a2ecb7602d9702bf77ed", "53e9a2acb7602d9702bb2d43", "53e9b0d1b7602d9703b4b4f6", "53e9b166b7602d9703beb51a", "53e9a63db7602d9702f69464", "55a3d3d9612ca6486879fadd", "53e9a27ab7602d9702b8148d", "53e9aea4b7602d97038ca8a6", "55a4a158240103289977f825", "53e9b768b7602d970430ca71", "55a43ea8612ca648688de68c", "53e9bb2fb7602d970476e478", "53e9b53cb7602d9704075793", "53e99800b7602d970200fbeb", "53e9b577b7602d97040b6f8a", "53e9bcadb7602d970492abdc"]}')
#formatNodes('{"id": "53e99837b7602d970205d328", "title": "Neurobiology of addiction", "authors": [{"name": "Roy A Wise", "org": "Department of Psychology, Concordia University, 1455 de Maisonneuve Boulevard West, Montreal, H3G 1M8 Canada"}], "venue": "Current Opinion in Neurobiology", "year": 1996, "keywords": ["nmda n -methyl- d -aspartate", "dpdpe [ d -pen 2", "damgo [ d -ala 2", "mk-801 methyl-dihydro-dibenzocyclohepten-imine", "cpp 3-(2-carboxypiperazin-4-yl)-propyl-l-phosphoric acid", "n -me-phe 4 -gly 5 -ol]-enkephalin", "d -pen 5 ]-enkephalin", "gaba \u03b3-aminobutyric acid"], "n_citation": 892, "page_start": "243", "page_end": "251", "lang": "en", "volume": "6", "issue": "2", "issn": "Current Opinion in Neurobiology", "doi": "10.1016/S0959-4388(96)80079-1", "url": ["http://dx.doi.org/10.1016/S0959-4388(96)80079-1"], "abstract": "Addictive drugs have habit-forming actions that can be localized to a variety of brain regions. Recent advances in our understanding of the chemical \u2018trigger zones\u2019 in which individual drugs of abuse initiate their habit-forming actions have revealed that such disparate drugs as heroin, cocaine, nicotine, alcohol, phencyclidine, and cannabis activate common reward circuitry in the brain. Although these drugs have many actions that are distinct, their habit-forming actions (and perhaps the relevant elements of their disparate withdrawal symptoms) appear to have a common denominator, namely, similar effects in the brain mechanisms of reward.", "references": ["53e99db8b7602d9702677660", "53e9a3abb7602d9702cb9db6", "53e9b59bb7602d97040e363b", "53e9b4efb7602d9704019f55", "53e9a22bb7602d9702b30286", "53e9aa95b7602d9703410333", "53e9a416b7602d9702d34666", "53e9af4cb7602d970398bc0e", "53e9ba54b7602d97046700c4", "53e9aab7b7602d9703432e47", "53e9b4a0b7602d9703faae9b", "53e9be64b7602d9704b26433", "53e9a29db7602d9702ba1af6", "53e99f8cb7602d970285ed22", "53e9a194b7602d9702a89bb7", "53e9ae90b7602d97038b3cfa", "53e999e0b7602d97022241c3", "53e9ba70b7602d9704690c6a", "53e9a17fb7602d9702a738f5", "53e9a495b7602d9702db59a1", "53e9987db7602d97020b8ffc", "53e99940b7602d970217f380", "53e9a2acb7602d9702bb49b0", "53e9b5c8b7602d9704113471", "53e9a570b7602d9702e98a5b", "55a452222401c6de3b8f3aca", "53e99df7b7602d97026ba2ac", "53e9b607b7602d970415d563", "53e99fa8b7602d970287c17e", "53e9b1ffb7602d9703c93661", "53e9b725b7602d97042bc61f", "53e99b9bb7602d9702442b03", "53e9a18db7602d9702a7e708", "53e9ad68b7602d9703751a27", "55a67345612ca6eebab09fb7", "53e9a3fbb7602d9702d12360", "53e9b7f5b7602d97043a3c13", "53e99cd9b7602d970258fab5", "53e9b49ab7602d9703fa1e1d", "53e9b6a2b7602d970421a14a", "53e9b3a4b7602d9703e89984", "53e9a8b0b7602d97031fda8a", "53e99c6eb7602d9702521c91", "53e9b483b7602d9703f870fc", "53e9b844b7602d9704404fdc", "53e9aae6b7602d9703468f66", "53e9b3b7b7602d9703e9fa4e", "53e9a1bcb7602d9702ab43ba", "53e99bb1b7602d970245a535", "53e9a930b7602d970327f989", "55a41d5a2401c6de3b832969", "53e9aed8b7602d9703904e14", "53e99d37b7602d97025ef9b1", "53e9b94db7602d9704539ed8", "53e9b495b7602d9703f9c8ed", "53e9b23ab7602d9703cd7b0d", "53e9a0cab7602d97029b38a1", "56d8f104dabfae2eee7512f8", "53e9ae4fb7602d970386aae8", "55a34fd8612ca6486868bbd6", "53e9b708b7602d970429ce76", "53e99c05b7602d97024b4405", "53e9b09fb7602d9703b0a24a", "53e9a60ab7602d9702f37eab", "53e99cedb7602d97025a3d59", "53e9b296b7602d9703d3fd79", "53e9ad04b7602d97036e07a2", "53e9bcfcb7602d9704982323", "53e9b1ddb7602d9703c6de33", "53e9aaf3b7602d9703471a33", "53e9b11cb7602d9703b98a95", "53e99db1b7602d970266f10f"]}')
#formatNodes('{"id": "53e99837b7602d970205d329", "title": "Non-opioid analgesics", "authors": [{"name": "Barbara J Pleuvry", "org": "is Senior Lecturer in Anaesthesia and Pharmacology at the University of Manchester, UK. She is a pharmacist by first degree but has been involved in teaching pharmacology to postgraduates and undergraduates for over 30 years. Her research interests include pain, analgesia and anticonvulsant drugs."}], "venue": "Anaesthesia & Intensive Care Medicine", "year": 2005, "keywords": ["cox", "celecoxib", "nsaids", "paracetamol", "dmards", "migraine", "arthritis", "analgesic", "tryptans", "pharmacology", "drug", "enzyme", "adverse effect"], "page_start": "25", "page_end": "29", "lang": "en", "volume": "6", "issue": "1", "issn": "Anaesthesia & Intensive Care Medicine", "doi": "10.1383/anes.6.1.25.57139", "url": ["http://dx.doi.org/10.1383/anes.6.1.25.57139"], "abstract": "The non-steroidal anti-inflammatory drugs (NSAIDs) and paracetamol produce analgesia by inhibition of one of the three isoforms of cyclo-oxygenase (COX), which converts arachidonic acid to the cyclic endoperoxides from which the prostanoids are formed. Many of the adverse effects of NSAIDs are mediated via COX-1 inhibition and more recent drugs, such as celecoxib, have selectivity for the COX-2 enzyme, which is induced during inflammation. These drugs cause fewer adverse gastric effects in patients without gastric pathology. Paracetamol has little anti-inflammatory action at therapeutic doses and has been shown to have selectivity for COX-3. While NSAIDs and paracetamol have a beneficial role in arthritic pain, disease-modifying anti-rheumatic drugs (DMARDs) have been recommended at an early stage in the development of the disease. Similarly NSAIDs and paracetamol are less commonly used to treat migraine since the introduction of the tryptans. Prophylactic treatment for migraine is recommended if the patient suffers more that five attacks per month.", "references": ["53e99a3cb7602d970229c7b1", "53e9bafbb7602d9704735a95", "53e9a0d8b7602d97029bfa8f"]}')
#formatNodes('{"id": "53e99837b7602d970205d32a", "title": "Neurobiology of ADHD.", "authors": [{"name": "Gail Tripp"}, {"name": "Jeffery R. Wickens", "org": "Neurobiology Research Unit, Okinawa Institute of Science and Technology, Japan"}], "venue": "Neuropharmacology", "year": 2009, "keywords": ["mechanism", "dopamine", "adhd", "reinforcement", "genetics"], "page_start": "579", "page_end": "589", "lang": "en", "volume": "57", "issue": "7-8", "issn": "1873-7064", "doi": "10.1016/j.neuropharm.2009.07.026", "url": ["http://dx.doi.org/10.1016/j.neuropharm.2009.07.026", "http://www.ncbi.nlm.nih.gov/pubmed/19627998?report=xml&format=text"], "abstract": "Attention-deficit hyperactivity disorder (ADHD) is a prevalent and debilitating disorder diagnosed on the basis of persistent and developmentally-inappropriate levels of overactivity, inattention and impulsivity. The etiology and pathophysiology of ADHD is incompletely understood. There is evidence of a genetic basis for ADHD but it is likely to involve many genes of small individual effect. Differences in the dimensions of the frontal lobes, caudate nucleus, and cerebellar vermis have been demonstrated. Neuropsychological testing has revealed a number of well documented differences between children with and without ADHD. These occur in two main domains: executive function and motivation although neither of these is specific to ADHD. In view of the recent advances in the neurobiology of reinforcement, we concentrate in this review on altered reinforcement mechanisms. Among the motivational differences, many pieces of evidence indicate that an altered response to reinforcement may play a central role in the symptoms of ADHD. In particular, sensitivity to delay of reinforcement appears to be a reliable finding. We review neurobiological mechanisms of reinforcement and discuss how these may be altered in ADHD, with particular focus on the neurotransmitter dopamine and its actions at the cellular and systems level. We describe how dopamine cell firing activity is normally associated with reinforcing events, and transfers to earlier time-points in the behavioural sequence as reinforcement becomes more predictable. We discuss how a failure of this transfer may give rise to many symptoms of ADHD, and propose that methylphenidate might act to compensate for the proposed dopamine transfer deficit.", "references": ["53e9b2c6b7602d9703d6fd50", "55a4589ec91b587b0978b1ff", "53e9ab69b7602d9703504408", "53e99e99b7602d9702760775", "55a48290612ca6486899054a", "53e9a6dfb7602d97030140c2", "53e9b488b7602d9703f8be30", "53e99a35b7602d9702290700", "53e9a237b7602d9702b3cb40", "53e9b7f5b7602d97043a400f", "53e99b5eb7602d97024045f2", "53e9a479b7602d9702d9760d", "53e9b8e1b7602d97044c47b2", "55a409ed612ca6486882547d", "53e9b360b7602d9703e3fa5d", "55a46bf5612ca648689617b3", "53e9bcefb7602d9704978970", "53e99a2fb7602d970228924b", "53e99a0eb7602d970225ead1", "55a450d92401c6de3b8f0cd7", "55a498d6c91bf3b1cc3fff41", "53e9abe5b7602d97035a1d3f", "55a35a1f24012c2ab7a7a973", "53e9b0eeb7602d9703b6c1ee", "53e9a098b7602d970297ff6d", "53e99b86b7602d970242d0de", "53e9b1a9b7602d9703c32e72", "53e99ad1b7602d9702352f96", "53e9bd50b7602d97049e1aad", "53e9b65bb7602d97041bc6b7", "53e9bbdbb7602d970482eefa", "53e9b5cfb7602d970411dbd3", "53e9a791b7602d97030cbf17", "56d818a5dabfae2eee83b597", "53e9a114b7602d9702a045da", "53e9a34ab7602d9702c52a7e", "53e9a922b7602d9703271ecb", "53e9adb6b7602d97037b8cd1", "53e9bd04b7602d97049892cc", "53e999e0b7602d97022241c3", "53e9b04eb7602d9703ab3a63", "53e9a958b7602d97032afa65", "53e99d7ab7602d9702633853", "53e99eb4b7602d970277c2f7", "53e9b0c7b7602d9703b3c4b1", "56d9102cdabfae2eee36694f", "53e9ad42b7602d97037272a9", "53e9a562b7602d9702e88201", "53e9aeb1b7602d97038d8220", "56d828f1dabfae2eeeef6e55", "53e9b60db7602d9704163992", "53e9b4eeb7602d97040178eb", "53e9b677b7602d97041df720", "53e9a246b7602d9702b4add1", "56d818e0dabfae2eee857ee4", "53e9bd82b7602d9704a26472", "53e9a6aeb7602d9702fe200e", "53e9b062b7602d9703ac9495", "53e99fa8b7602d970287c2ed", "53e9b815b7602d97043caa48", "53e99fc9b7602d97028a66af", "53e9ad87b7602d970377f854", "56d9023ddabfae2eeedf21e6", "53e9a2acb7602d9702bb6123", "53e9a727b7602d970305ce3a", "53e99b51b7602d97023f5dc4", "55a46ac6612ca6486895e86e", "53e99bb1b7602d9702457552", "53e99beab7602d97024958a2", "55a3d6b3c91b587b096408f2", "53e9a1e7b7602d9702ae5eb6", "53e9bc1bb7602d9704885673", "55a4cb0624011b361acdaf5b", "53e9b0d8b7602d9703b56a6d", "53e998d5b7602d970210fd25", "53e9a350b7602d9702c594dd", "53e9ac95b7602d970366e142", "53e9b05cb7602d9703ac0355", "53e9bbeab7602d970483f390", "53e9b648b7602d97041a92bf", "53e9a6dfb7602d9703012644", "53e9bc54b7602d97048cff1a", "53e99dd3b7602d9702692072", "53e9b13eb7602d9703bc18a5", "53e9b2bfb7602d9703d6985d", "53e9baecb7602d970471ef07", "53e9bc80b7602d970490032d", "53e9adaab7602d97037ab20f", "53e99dd3b7602d9702695975", "55a40442612ca6486881521d", "53e9b839b7602d97043f7edf", "53e9b40eb7602d9703f01831", "53e9b6b4b7602d9704237c6d", "53e9ba28b7602d9704631191", "56d82b97dabfae2eee0046e6", "53e9a381b7602d9702c91d8a", "53e9af99b7602d97039e55b0", "53e9a00ab7602d97028eeb7a", "53e9bd04b7602d970498df92", "53e9b81cb7602d97043d3930", "56d9102adabfae2eee365f76", "53e9b6d1b7602d970425db59", "53e9bcdab7602d9704961944", "55a4363e2401c6de3b88d52d", "53e9add4b7602d97037deb84", "53e9bc61b7602d97048d8113", "53e9baecb7602d970471f731", "53e9a31fb7602d9702c29e81", "55a3fc2bc91b587b0968f0e4", "53e9996eb7602d97021ae049", "53e9b90bb7602d97044f3831", "53e9b4c9b7602d9703fe4f4a", "53e99998b7602d97021dbe29", "53e9b413b7602d9703f09ef9", "53e9b6a6b7602d970422076c", "53e9a92ab7602d9703278434", "55a571c524012c2a39243e5a", "53e9b8e1b7602d97044c60df", "53e9b63bb7602d9704199dd9", "53e99bfeb7602d97024a736b", "56d82b96dabfae2eee003de6", "53e9b409b7602d9703efed86", "53e9a58cb7602d9702eb5c98", "53e9a8f8b7602d9703246625", "56d8187edabfae2eee8277fd", "53e9a525b7602d9702e480af", "53e998bfb7602d97020fa7f6", "53e9af2db7602d9703966a2e", "55a39ee0c91b587b095d008e"]}')
#formatNodes('{"id": "53e99837b7602d970205d32b", "title": "New Orleans asthma", "authors": [{"name": "John Salvaggio", "org": "From the United States Public Health Service National Center for Air Pollution Control New Orleans, La. USA"}, {"name": "John Seabury", "org": "From the United States Public Health Service National Center for Air Pollution Control New Orleans, La. USA"}], "venue": "The Journal of Allergy and Clinical Immunology", "year": 1971, "page_start": "82", "page_end": "95", "lang": "en", "volume": "48", "issue": "2", "issn": "The Journal of Allergy and Clinical Immunology", "doi": "10.1016/0091-6749(71)90090-X", "abstract": "A semiquantitative survey of atmospheric spore concentrations in the city of New Orleans with the use of automatic intermittent rotoslide samplers was performed during the years 1967 and 1968. In comparison with our previous rotoslide pollen survey, spores were invariably detected in excess of pollen grains by a factor of 10 to 100. Relatively large spores of the deuteromycetes (fungi imperfecti) were easily identified morphologically. Identification of small spores was uncertain because of considerable group overlap and interspecies variation. Spores in this category were detected in highest quantity. Spores resembling large basidiospores were included in a third general category. Many myxomycete spores were also likely included in this category because of similar morphology. In all morphological categories, semiquantitative atmospheric spore counts were comparatively low in January and February. Counts increased sharply in March and April and increased variably throughout the summer and late fall months. Noticeable decreases were recorded in late November at or near the usual onset of local killing frosts. Petri plate colony identification, although performed only sporadically, was not as helpful as anticipated. Analysis of one typical large asthma epidemic (December, 1968) revealed high rotoslide catches in all major spore categories but no sharp increase in total cultural colony count or obvious change in colony composition."}')

formatNodes('{"id": "53e99837b7602d970205d324", "title": "Network-Oblivious Algorithms.", "authors": [{"name": "Gianfranco Bilardi"}, {"name": "Andrea Pietracaprina"}, {"name": "Geppino Pucci"}, {"name": "Michele Scquizzato"}, {"name": "Francesco Silvestri"}], "venue": "international parallel and distributed processing symposium", "year": 2007, "keywords": ["any machines", "are nevertheless ecient", "computational modeling", "space technology", "computer networks", "computational complexity", "parallel algorithms", "concurrent computing", "model of computation", "bandwidth", "parallel processing", "algorithm design and analysis"], "n_citation": 21, "page_start": "1", "page_end": "10", "lang": "en", "volume": "abs/1404.3318", "doi": "10.1109/IPDPS.2007.370243", "url": ["http://dx.doi.org/10.1109/IPDPS.2007.370243", "http://arxiv.org/abs/1404.3318"], "references": ["53e9b110b7602d9703b9057d", "53e9b71db7602d97042b5023", "53e9ac4eb7602d970362122d", "53e99809b7602d970201cb83", "53e999ffb7602d970224a87d", "56d8fed2dabfae2eeec9f99e", "53e9b70fb7602d97042a59fe", "53e9ab4fb7602d97034e0e96", "53e9a540b7602d9702e65cd0", "53e9aadfb7602d97034623d0", "53e9ab3db7602d97034caffd", "53e9a855b7602d970319d0c2", "53e9ac75b7602d9703648e12", "53e9bbc2b7602d970481144f", "53e999ffb7602d970224dbf8", "53e9bc10b7602d97048758c9", "53e9b797b7602d9704340043", "53e9ab69b7602d9703505fec", "53e9a8ffb7602d970324d8f5", "53e9a246b7602d9702b4bd96", "53e9b923b7602d970450ffba", "53e9aadfb7602d9703461d05", "53e999fab7602d9702243d88", "53e9b74bb7602d97042ea295", "53e999ffb7602d970224dbf9", "56d8141bdabfae2eee65e9a5", "53e99837b7602d970205d324", "53e9a9ebb7602d970334dd36", "53e9af99b7602d97039e3edc", "53e9b976b7602d970456398f", "53e99f4fb7602d9702820cb7", "53e9a0adb7602d97029959f4", "53e99960b7602d97021a3a5e"]}')

#with open("data1.txt", 'r+') as f:
#    lines = f.readlines()

#for line in lines:
    # print("---------------------\n")
    # print(line)
#    line = line.replace("'", "''")
#    formatNodes(line )

# Scenario
# 1 - Latest papers by author
# 2 - latest papers by topic