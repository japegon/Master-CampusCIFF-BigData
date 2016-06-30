"""
@author: U{Jose Luis Gonzalez Blazquez}
@version: 2.0
@since: 30Jun2016
"""

__version__ = '2.0'
__modified__ = '30Jun2016'
__author__ = 'Jose Luis Gonzalez Blazquez'
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF, N3
import xml.dom.minidom


def getLocalLabel (instancia):
 	sparqlSesame = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/SocialNetwork", returnFormat=JSON)
	queryString = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX sn: <http://ciff.curso2015/ontologies/owl/socialNetwork#> SELECT ?label WHERE { sn:" + instancia + " rdfs:label ?label }"
	sparqlSesame.setQuery(queryString)
	sparqlSesame.setReturnFormat(JSON)
	query   = sparqlSesame.query()
	results = query.convert()
	devolver = []
	for result in results["results"]["bindings"]:
		label = result["label"]["value"]
		if 'xml:lang' in result["label"]:
			lang = result["label"]["xml:lang"]
		else:
			lang = None
		print "The label: " + label
		if 'xml:lang' in result["label"]:
			print "The lang: " + lang
		devolver.append((label, lang))
	return devolver
	

# Inserta una tripleta en una instancia
def updateLocalLabel (instancia, resource, label, objeto):
	sparqlSesame = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/SocialNetwork/statements", returnFormat=XML)
	sparqlSesame.method = 'POST'
	prefixString = "PREFIX sn: <http://ciff.curso2015/ontologies/owl/socialNetwork#> "
	prefixString += "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
	prefixString += "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
	prefixString += "PREFIX foaf: <http://xmlns.com/foaf/0.1/> "
	queryString = prefixString + "INSERT DATA { GRAPH sn:" + instancia + " { <" + resource + "> <" + label + "> " + objeto + " } }"
	sparqlSesame.setQuery(queryString)
	sparqlSesame.query()
	print "Insertado: " + "<" + resource + "> <" + label + "> " + objeto + " "

	
def getDataFromResource (resource, lang, instancia, endpoint):
	wrapper = SPARQLWrapper(endpoint)
	sparqlDBPedia = SPARQLWrapper(endpoint)

	if (endpoint == 'http://dbpedia.org/sparql'):
		prefixString = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> "
		
		strStartFilter = "FILTER(STRSTARTS(STR(?label), \"http://dbpedia.org/property\") || STRSTARTS(STR(?label), \"http://dbpedia.org/ontology\"))"
	
	elif (endpoint == 'http://data.linkedmdb.org/sparql'):
		prefixString = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
		prefixString += "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> "
		prefixString += "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
		prefixString += "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
		prefixString += "PREFIX foaf: <http://xmlns.com/foaf/0.1/> "
		prefixString += "PREFIX oddlinker: <http://data.linkedmdb.org/resource/oddlinker/> "
		prefixString += "PREFIX map: <file:/C:/d2r-server-0.4/mapping.n3#> "
		prefixString += "PREFIX db: <http://data.linkedmdb.org/resource/> "
		prefixString += "PREFIX dbpedia: <http://dbpedia.org/property/> "
		prefixString += "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> "
		prefixString += "PREFIX dc: <http://purl.org/dc/terms/> "
		prefixString += "PREFIX movie: <http://data.linkedmdb.org/resource/movie/> "
		
		strStartFilter = ""
	
	elif (endpoint == 'http://webenemasuno.linkeddata.es/sparql'):
		prefixString = "PREFIX opmopviajero: <http://webenemasuno.linkeddata.es/ontology/OPMO/> "
		prefixString += "PREFIX sioc: <http://rdfs.org/sioc/ns#> "
		prefixString += "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
		prefixString += "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
		prefixString += "PREFIX foaf: <http://xmlns.com/foaf/0.1/> "
		
		strStartFilter = ""
	
	else:
		#Enviar excepcion
		print "Endpoint no definido";
	
	
	if (lang):
		queryString = prefixString + "SELECT DISTINCT ?label ?o WHERE { <" + resource + "> ?label ?o " + strStartFilter + " FILTER (!isLiteral(?o) || lang(?o)=\"\" || langMatches( lang(?o),\"" + lang +"\" )) }"
	else:
		queryString = prefixString + "SELECT DISTINCT ?label ?o WHERE { <" + resource + "> ?label ?o " + strStartFilter + " }"

	wrapper.setReturnFormat(JSON)
	wrapper.setQuery(queryString)
	results = wrapper.query().convert()
		
	print '\n\n*** Resultado de la query'
	for result in results["results"]["bindings"]:
		label = result["label"]["value"]
		objeto = result["o"]["value"]
		objeto_tipo = result["o"]["type"]
		#objeto_datatype = result["o"]["datatype"]
		if (objeto_tipo == 'uri'):
			objeto = "<" + objeto + ">"			
		else:
			objeto = objeto.replace('"','\\"')
			objeto = objeto.replace("\n"," ")
			objeto = "\"" + objeto + "\""
			if (objeto_tipo == 'typed-literal'):
				datatype = result["o"]["datatype"]
				datatype = "<" + datatype + ">"
				objeto += "^^" + datatype
			if ((objeto_tipo == 'literal') and 'xml:lang' in result["o"]):
				objeto += "@" + result["o"]["xml:lang"]
		print "-------"
		updateLocalLabel(instancia, resource, label, objeto)
		print "-------"

	
def getDBpediaResource (label, lang, endpoint):
	sparqlDBPedia = SPARQLWrapper(endpoint)
	if (lang):
		queryString = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?s WHERE { ?s rdfs:label \"" + label + "\"@" +lang + " . ?s rdf:type foaf:Person} " 
	else:
		queryString = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?s WHERE { ?s rdfs:label \"" + label + "\" . ?s rdf:type foaf:Person } " 
	
	sparqlDBPedia.setQuery(queryString)
	sparqlDBPedia.setReturnFormat(JSON)
	query   = sparqlDBPedia.query()
	results = query.convert()
	
	for result in results["results"]["bindings"]:
		resource = result["s"]["value"]
		print "The resource: " + resource
		print "-------"
		getDataFromResource(resource, lang, "instancia1", endpoint)
		print "-------"

		
def getLinkedmdbResource (label, lang, endpoint):
	sparqlLinkedmdb = SPARQLWrapper(endpoint)

	prefixString = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
	prefixString += "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> "
	prefixString += "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
	prefixString += "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
	prefixString += "PREFIX foaf: <http://xmlns.com/foaf/0.1/> "
	prefixString += "PREFIX oddlinker: <http://data.linkedmdb.org/resource/oddlinker/> "
	prefixString += "PREFIX map: <file:/C:/d2r-server-0.4/mapping.n3#> "
	prefixString += "PREFIX db: <http://data.linkedmdb.org/resource/> "
	prefixString += "PREFIX dbpedia: <http://dbpedia.org/property/> "
	prefixString += "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> "
	prefixString += "PREFIX dc: <http://purl.org/dc/terms/> "
	prefixString += "PREFIX movie: <http://data.linkedmdb.org/resource/movie/> "
	prefixString += "PREFIX lang: <http://www.lingvoj.org/lingvo/> "

	if (lang):
		queryString = prefixString + "SELECT ?m WHERE { ?m rdfs:label \"" + label + "\"@" + lang + " . ?m rdf:type movie:film }"
	else:
		queryString = prefixString + "SELECT ?m WHERE { ?m rdfs:label \"" + label + "\" . ?m rdf:type movie:film} "
	
	sparqlLinkedmdb.setQuery(queryString)
	sparqlLinkedmdb.setReturnFormat(JSON)
	query   = sparqlLinkedmdb.query()
	results = query.convert()
	
	for result in results["results"]["bindings"]:
		resource = result["m"]["value"]
		print "->The resource: " + resource
		print "-------"
		getDataFromResource(resource, lang, "instancia3", endpoint)
		print "-------"


def getWebenemasunoResource (label, lang, endpoint):
	sparqlWebenemasuno = SPARQLWrapper(endpoint)
	if (lang):
		queryString = "PREFIX opmopviajero: <http://webenemasuno.linkeddata.es/ontology/OPMO/> PREFIX sioc: <http://rdfs.org/sioc/ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?r WHERE {?r sioc:title \"" + label + "\"@" + lang + " . ?r rdf:type opmopviajero:Guide}"
	else:
		queryString = "PREFIX opmopviajero: <http://webenemasuno.linkeddata.es/ontology/OPMO/> PREFIX sioc: <http://rdfs.org/sioc/ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?r WHERE {?r sioc:title \"" + label + "\" . ?r rdf:type opmopviajero:Guide}"
	sparqlWebenemasuno.setQuery(queryString)
	sparqlWebenemasuno.setReturnFormat(JSON)
	query   = sparqlWebenemasuno.query()
	results = query.convert()
	
	for result in results["results"]["bindings"]:
		resource = result["r"]["value"]
		print "->The resource: " + resource
		print "-------"
		getDataFromResource(resource, lang, "instancia4", endpoint)
		print "-------"
		

if __name__ == '__main__':
	# getLocalLabel devuelve una lista con todas las instancias que haya con sus label y lang
	# y luego se hace la llamada al repositorio externo para enriquecer cada combinacion de label-lang recibida
	lista = getLocalLabel("instancia1");
	print lista
	endpoint = 'http://dbpedia.org/sparql';
	for result in lista:
		(label, lang) = result
		resource = getDBpediaResource (label, lang, endpoint)

	print "\n---------------------\n"

	lista = getLocalLabel("instancia3");
	print lista
	endpoint = 'http://data.linkedmdb.org/sparql';
	for result in lista:
		(label, lang) = result
		resource = getLinkedmdbResource (label, lang, endpoint);

	print "\n---------------------\n"

	lista = getLocalLabel("instancia4");
	print lista
	endpoint = 'http://webenemasuno.linkeddata.es/sparql';
	for result in lista:
		(label, lang) = result
		resource = getWebenemasunoResource (label, lang, endpoint);

	print "\n---------------------\n"

