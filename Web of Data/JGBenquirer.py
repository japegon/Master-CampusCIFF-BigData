"""
@author: U{Jose Luis Gonzalez Blazquez}
@version: 0.3
@since: 28Jun2015
"""

__version__ = '0.3'
__modified__ = '28Jun2015'
__author__ = 'Jose Luis Gonzalez Blazquez'
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import xml.dom.minidom



def getLocalLabel (instancia):
 
 	sparqlSesame = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/SocialNetwork",  returnFormat=JSON)
	queryString = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX sn:  <http://ciff.curso2015/ontologies/owl/socialNetwork#> SELECT ?label WHERE { sn:" + instancia + " rdfs:label ?label }"
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

		
def getLinkedmdbResource (label, lang, endpoint):

	sparqlLinkedmdb = SPARQLWrapper(endpoint)

	if (lang):
		queryString = "PREFIX movie: <http://data.linkedmdb.org/resource/movie/> PREFIX lang: <http://www.lingvoj.org/lingvo/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?m WHERE { ?m rdfs:label \"" + label + "\" . ?m rdf:type movie:film . ?m movie:language lang:" + lang + " }"
	
	else:
		queryString = "PREFIX movie: <http://data.linkedmdb.org/resource/movie/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?m WHERE { ?m rdfs:label \"" + label + "\" . ?m rdf:type movie:film} "
	
	sparqlLinkedmdb.setQuery(queryString)
	sparqlLinkedmdb.setReturnFormat(JSON)
	query   = sparqlLinkedmdb.query()
	results = query.convert()
	print
	for result in results["results"]["bindings"]:
		resource = result["m"]["value"]
		print "->The resource: " + resource
		

def getWebenemasunoResource (label, lang, endpoint):

	sparqlWebenemasuno = SPARQLWrapper(endpoint)
	if (lang):
		queryString = "PREFIX opmopviajero: <http://webenemasuno.linkeddata.es/ontology/OPMO/> PREFIX sioc: <http://rdfs.org/sioc/ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?r WHERE {?r sioc:title \"" + label + "\" . ?r opmopviajero:language \"" + lang + "\" . ?r rdf:type opmopviajero:Guide}"
	else:
		queryString = "PREFIX opmopviajero: <http://webenemasuno.linkeddata.es/ontology/OPMO/> PREFIX sioc: <http://rdfs.org/sioc/ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?r WHERE {?r sioc:title \"" + label + "\" . ?r rdf:type opmopviajero:Guide}"
	sparqlWebenemasuno.setQuery(queryString)
	sparqlWebenemasuno.setReturnFormat(JSON)
	query   = sparqlWebenemasuno.query()
	results = query.convert()
	print
	for result in results["results"]["bindings"]:
		resource = result["r"]["value"]
		print "->The resource: " + resource
		

if __name__ == '__main__':

	# getLocalLabel devuelve una lista con todas las instancias que haya con sus label y lang
	# y luego se hace la llamada al repositorio externo para enriquecer cada combinacion de label-lang recibida
	lista = getLocalLabel("instancia1");
	print lista
	endpoint = 'http://dbpedia.org/sparql';
	for result in lista:
		(label, lang) = result
		resource = getDBpediaResource (label, lang, endpoint);

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

	