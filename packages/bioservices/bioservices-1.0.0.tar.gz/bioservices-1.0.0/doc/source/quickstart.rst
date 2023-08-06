.. _quickstart:

Quick Start
#################

**BioServices** provides access to several Web Services. Each service requires some expertise on its own. 
In this Quick Start section, we will neither cover all the services nor all their functionalities. However,
it should give you a good overview of what you can do with BioServices (both from the user and developer point of views).


Before starting, let us remind what are Web Services. There provide an access to databases or applications via a web interface based on the SOAP/WSDL or the REST technologies. These technologies allow a programmatic access, which we take advantage in BioServices.

The REST technology uses URLs so there is no external dependency. 
You simply need to build a well-formatted URL and you will retrieve
an XML document that you can consume with your preferred technology
platform.

The SOAP/WSDL technology combines SOAP (Simple Object Access Protocol), which is
a messaging protocol for transporting information and the WSDL (Web Services
Description Language), which is a method for describing Web Services and their
capabilities.

Let us look at some of the Web Services wrapped in BioServices.

Kegg service
=============
.. testsetup:: kegg

    from bioservices import Kegg
    k = Kegg(verbose=False)

Start a KEGG interface::

    from bioservices import Kegg
    k = Kegg(verbose=False)

There are 5-6 main functions (e.g., :meth:`~bioservices.kegg.Kegg.list`) 
that allow access to the KEGG database. 

You can use the :meth:`~bioservices.kegg.Kegg.info` to obtain statistics on the
**pathway** database::

    >>> print k.info("pathway")
    pathway          KEGG Pathway Database
    path             Release 65.0+/01-15, Jan 13
                     Kanehisa Laboratories
                     218,277 entries

You can see the list of valid databases using the databases method. Each of the
database entry can also be listed using the :meth:`~bioservices.kegg.Kegg.list`
method. For instance, the organisms can be retrieved with::

    k.list("organism")

However, to extract the Ids exta processing is required. So, we provide aliases 
to retrieve the organism Ids::

    k.organismIds

The human organism is coded as "hsa". You can also get the T number instead of
Ids:

.. doctest:: kegg

    >>> k.code2Tnumber("hsa")
    'T01001'


Every elements is referred to with a Kegg ID, which may be difficult to handle
at first. There are methods to retrieve the IDs though. For instance, get the list of 
pathways ids for the current organism as follows::

    k.pathwayIds

For a given gene, you can get the full information related to that gene by using
the method :meth:`~bioservices.kegg.Kegg.get`::

    print k.get("hsa:3586")

or a pathway::

    print k.get("path:hsa05416")

An additional class :class:`~bioservices.kegg.KeggParser` will help you to convert any KEGG ouput returned
by the get method into a dictionary.


.. seealso:: Reference guide of :class:`bioservices.kegg.Kegg` for more details
.. seealso:: Reference guide of :ref:`kegg_tutorial` for more details
.. seealso:: Reference guide of :class:`bioservices.kegg.KeggParser` for more details

.. WSDbfetch service
   ==================
   There is a uniprot module that allows to access to the uniprot WSDL. However,
   there are really few services and the only relevant method returns raw data that
   the user will need to scan. For instance::

..    >>> from bioservices import WSDbfetch
    >>> w = WSDbfetch()
    >>> data = w.fetchBatch("uniprot", "zap70_human", "xml", "raw")

.. .. seealso:: Reference guide of :class:`bioservices.wsdbfetch.WSDbfetch` for more details


UniProt service
================

With this module, you can map an ID from a database to another one. For instance
to convert the UniProtKB ID into KEGG ID, use:

.. doctest::

    >>> from bioservices.uniprot import UniProt
    >>> u = UniProt(verbose=False)
    >>> u.mapping(fr="ACC", to="KEGG_ID", query='P43403')
    ['From:ACC', 'To:KEGG_ID', 'P43403', 'hsa:7535']

Note that the returned response from uniprot web service is converted into a list.

You can also search for a specific UniProtKB id to get exhaustive information
about an ID::

    >>> res = u.searchUniProtId("P09958", format="xml")
    >>> u.searchUniProtId("P09958", format="fasta")
    '>sp|P09958|FURIN_HUMAN Furin OS=Homo sapiens GN=FURIN PE=1SV=2\nMELRPWLLWVVAATGTLVLLAADAQGQKVFTNTWAVRIPGGPAVANSVARKHGFLNLGQI\nFGDYYHFWHRGVTKRSLSPHRPRHSRLQREPQVQWLEQQVAKRRTKRDVYQEPTDPKFPQ\nQWYLSGVTQRDLNVKAAWAQGYTGHGIVVSILDDGIEKNHPDLAGNYDPGASFDVNDQDP\nDPQPRYTQMNDNRHGTRCAGEVAAVANNGVCGVGVAYNARIGGVRMLDGEVTDAVEARSL\nGLNPNHIHIYSASWGPEDDGKTVDGPARLAEEAFFRGVSQGRGGLGSIFVWASGNGGREH\nDSCNCDGYTNSIYTLSISSATQFGNVPWYSEACSSTLATTYSSGNQNEKQIVTTDLRQKC\nTESHTGTSASAPLAAGIIALTLEANKNLTWRDMQHLVVQTSKPAHLNANDWATNGVGRKV\nSHSYGYGLLDAGAMVALAQNWTTVAPQRKCIIDILTEPKDIGKRLEVRKTVTACLGEPNH\nITRLEHAQARLTLSYNRRGDLAIHLVSPMGTRSTLLAARPHDYSADGFNDWAFMTTHSWD\nEDPSGEWVLEIENTSEANNYGTLTKFTLVLYGTAPEGLPVPPESSGCKTLTSSQACVVCE\nEGFSLHQKSCVQHCPPGFAPQVLDTHYSTENDVETIRASVCAPCHASCATCQGPALTDCL\nSCPSHASLDPVEQTCSRQSQSSRESPPQQQPPRLPPEVEAGQRLRAGLLPSHLPEVVAGL\nSCAFIVLVFVTVFLVLQLRSGFSFRGVKVYTMDRGLISYKGLPPEAWQEECPSDSEEDEG\nRGERTAFIKDQSAL\n'


.. seealso:: Reference guide of :class:`bioservices.uniprot.UniProt` for more details

QuickGO
=========

To acces to the GO interface, simply create an instance and look for a entry
using the :meth:`bioservices.quickgo.QuickGO.Term` method:

.. doctest::

    >>> from bioservices import QuickGO
    >>> g = QuickGO(verbose=False)
    >>> res = g.Term("GO:0003824")

.. seealso:: Reference guide of :class:`bioservices.quickgo.QuickGO` for more details

PICR service
=============


PICR, the Protein Identifier Cross Reference service provides 2 services
in WSDL and REST protocols. We implemented only the REST interface. The
methods available in the REST service are very similar to those available
via SOAP except for one major difference: only one accession or sequence
can be mapped per request.


The following example returns a XML document containing information about the
protein P29375 found in two specific databases::

    >>> from bioservices.picr import PICR
    >>> p = PICR()
    >>> res = p.getUPIForAccession("P29375", ["IPI", "ENSEMBL"])
    

.. seealso:: Reference guide of :class:`bioservices.picr.PICR` for more details


Biomodels service
===================

You can access the biomodels service and obtain a model as follows::


    >>> from bioservices import biomodels
    >>> b = biomodels.BioModels()
    >>> model = b.getModelSBMLById('BIOMD0000000299')

Then you can play with the SBML file with your favorite SBML tool.

In order to get the model IDs, you can look at the full list::

    >>> b.modelsId

Of course it does not tell you anything about a model; there are more useful functions such as 
:meth:`~bioservices.biomodels.getModelsIdByUniprotId` and others from the getModelsIdBy family.


.. seealso:: Reference guide of :class:`bioservices.biomodels.BioModels` for more details

Rhea service 
==============

Create a :class:`~bioservices.rhea.Rhea` instance as follows:

.. doctest::

    from bioservices import Rhea
    r = Rhea()

Rhea provides only 2 type of requests with a REST interface that are available with the :meth:`~bioservices.rhea.Rhea.search` and :meth:`~bioservices.rhea.Rhea.entry` methods. Let us first find information about the chemical product **caffein** using the :meth:`search` method::

    xml_response = r.search("caffein*")

The output is in XML format. Python provides lots of tools to deal with xml so
you can surely find good tools. 


Within bioservices, we wrap all returned XML documents into a BeautifulSoup
object that ease the manipulation of XML documents.

As an example, we can extract all fields "id" as follows::

    >>> [x.getText() for x in xml_response.findAll("id")]
    [u'27902', u'10280', u'20944', u'30447', u'30319', u'30315', u'30311', u'30307']

The second method provided is the :meth:`entry` method. Given an Id, 
you can query the Rhea database using Id found earlier (e.g., 10280)::

    >>> xml_response = r.entry(10280, "biopax2")

.. warning:: the r.entry output is also in XML format but we do not provide a
   specific XML parser for it unlike for the "search" method.

output format can be found in ::

    >>> r.format_entry
    ['cmlreact', 'biopax2', 'rxn']


.. seealso:: Reference guide of :class:`bioservices.rhea.Rhea` for more details

Create your own wrapper around WSDL service
==============================================

If a web service interface is not provided within bioservices, you can still easily access its functionalities. As an example, let us look at the `Ontology Lookup service <http://www.ebi.ac.uk/ontology-lookup/WSDLDocumentation.do>`_, which provides a WSDL service. In order to easily access this service, use the :class:`WSDLService` class as follows::

    >>> from bioservices import WSDLService
    >>> ols = WSDLService("OLS", " http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl")

You can now see which methods are available::

    >>> ols.methods

and call one (getVersion) using the :meth:`bioservices.services.WSDLService.serv`::

    >>> ols.serv.getVersion()

You can then look at something more complex and extract relevant information::

    >>> [x.value for x in ols.serv.getOntologyNames()[0]]

Of course, you can add new methods to ease the access to any functionalities::

    >>> ols.getOnlogyNames() # returns the values
