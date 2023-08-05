======================
ztfy.thesaurus package
======================


Introduction
------------

This package is made of a small set of classes which can be used to handle content's
indexation throught a controlled catalog of words called a *thesaurus*.

A thesaurus is specific in several manners, including:

- terms are structured in a hierarchy, where **generic** terms are linked to **specific**
terms

- terms synonyms are handled in the catalog.

A thesaurus can also be used at search time, for example to search contents on the base of
user's entered words but also on their synonyms or specific terms.


Initializing
------------

We first have to initialize our environment:

    >>> import zope.component
    >>> import zope.interface

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from ztfy.thesaurus.thesaurus import Thesaurus
    >>> zope.interface.classImplements(Thesaurus, IAttributeAnnotatable)
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> zope.component.provideAdapter(AttributeAnnotations)
    >>> from zope.location.traversing import LocationPhysicallyLocatable
    >>> zope.component.provideAdapter(LocationPhysicallyLocatable)

    >>> from ztfy.thesaurus.interfaces.loader import IThesaurusLoader
    >>> from ztfy.thesaurus.loader.config import ThesaurusLoaderConfiguration
    >>> from ztfy.thesaurus.loader.skos import SKOSThesaurusLoader
    >>> skos_loader = SKOSThesaurusLoader()
    >>> zope.component.provideUtility(skos_loader, IThesaurusLoader, 'skos')

    >>> from zope.schema.vocabulary import getVocabularyRegistry
    >>> from ztfy.i18n.languages import BaseLanguagesVocabulary
    >>> registry = getVocabularyRegistry()
    >>> registry.register('ZTFY base languages', BaseLanguagesVocabulary)

    >>> from ztfy.thesaurus.vocabulary import ThesaurusExtractsVocabulary
    >>> registry.register('ZTFY thesaurus extracts', ThesaurusExtractsVocabulary)

    >>> from ztfy.thesaurus.thesaurus import ThesaurusExtractsFactory
    >>> zope.component.provideAdapter(ThesaurusExtractsFactory)


Creating a thesaurus from a SKOS RDF file
-----------------------------------------

A thesaurus is a persistent object stored in the Zope Object DataBase and recorded as a named
utility ; a thesaurus is also a btree-based container which will contain terms and handle it's
own "private" catalog.

The quickest way to fill a thesaurus is done by importing contents of an XML file containing
thesaurus terms; several formats are available:

    >>> import os
    >>> datafile = os.path.join(current_dir, '..', 'doctests', 'data', 'SAMPLE1.xml')
    >>> data = open(datafile)
    >>> loader = SKOSThesaurusLoader()
    >>> thesaurus = loader.load(data)

When the thesaurus is loaded, we can get access to it's description and terms:

    >>> thesaurus.title
    u"Th\xe9saurus Naturaliste de l'Office National des For\xeats"
    >>> thesaurus.description
    u" Th\xe9saurus des r\xe9seaux naturalistes de l'Office National des For\xeats. "
    >>> thesaurus.created
    datetime.date(2011, 6, 1)

    >>> thesaurus.language
    'fr'
    >>> len(thesaurus.terms)
    2981

Top terms are those which are at the first level of the hierarchy and don't have any generic
term and which are parented to themselves:

    >>> len(thesaurus.top_terms)
    9

    >>> sorted([term.label for term in thesaurus.top_terms])
    [u'Ecologie des esp\xe8ces', u'Environnement', u'Habitat', u'Index g\xe9ographique', u'Intervention humaine',
    u'Mots-outils', u'M\xe9thodologie naturaliste', u"Protection de l'environnement", u"Science de l'environnement"]

    >>> thesaurus.terms.get(u'Environnement').generic is None
    True

    >>> thesaurus.terms.get(u'Environnement').parent.label
    u'Environnement'

    >>> thesaurus.terms.get(u'Intensification').parent.label
    u'Intervention humaine'

    >>> sorted([term.label for term in thesaurus.terms.get(u'Intensification').specifics])
    []

So a given term can be linked directly to only one generic and zero or more specific terms, to create a hierarchy:

    >>> thesaurus.terms.get(u'Intensification').generic.label
    u'Surexploitation de la nature'

    >>> sorted([term.label for term in thesaurus.terms.get(u'Surexploitation de la nature').specifics])
    [u'Agriculture intensive', u'D\xe9forestation', u'D\xe9gradation du sol', u'D\xe9sertification',
    u'Intensification', u'Surp\xeache']

It's then possible to get a term's parents ; result is ordered, from first to last parent:

    >>> [term.label for term in thesaurus.terms.get(u'Surexploitation de la nature').getParents()]
    [u'Impact des activit\xe9s humaines', u'Intervention humaine']

The "level" of a term is his depth in the hierarchy
    >>> thesaurus.terms.get(u'Surexploitation de la nature').level
    3

To get "brothers" of a term:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Surexploitation de la nature').getParentChilds()])
    [u'Anthropisation', u'S\xe9quelle de guerre']

And to get the full sub-hierarchy of a given term:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Surexploitation de la nature').getAllChilds()])
    [u'Agriculture intensive', u'D\xe9boisement', u'D\xe9forestation', u'D\xe9frichement',
    u'D\xe9gradation du sol', u'D\xe9sertification', u'Epuisement du sol', u'Erosion',
    u'Intensification', u'Surpat\xfbrage', u'Surp\xeache', u'Tassement du sol']

A term can also be associated to several terms, outside it's hierarchy or not:

    >>> sorted([term.label for term in thesaurus.terms.get(u'D\xe9forestation').associations])
    [u'Destruction de l\u2019habitat', u'D\xe9gradation des for\xeats', u'Exploitation foresti\xe8re',
    u'For\xeat', u"R\xe9duction de l'habitat"]


Creating a thesaurus from a SuperDoc export thesaurus file
----------------------------------------------------------

SuperDoc is a custom application used to handle bibliographic references, which handles thesauri and have a
custom export format in XML.

The Superdoc loader uses the same interface, but a configuration is required to define thesaurus language:

    >>> from ztfy.thesaurus.loader.config import ThesaurusLoaderConfiguration
    >>> from ztfy.thesaurus.loader.superdoc import SuperdocThesaurusLoader

    >>> datafile = os.path.join(current_dir, '..', 'doctests', 'data', 'SAMPLE2.xml')
    >>> data = open(datafile)
    >>> config = ThesaurusLoaderConfiguration()
    >>> config.language = u'fr'
    >>> loader = SuperdocThesaurusLoader()
    >>> thesaurus = loader.load(data, config)

    >>> thesaurus.language
    'fr'
    >>> len(thesaurus.terms)
    2472

Top terms are those which are at the first level of the hierarchy and don't have any generic
term and which are parented to themselves:

    >>> len(thesaurus.top_terms)
    465

    >>> sorted([term.label for term in thesaurus.top_terms])
    [u'Abri', u'Accident du travail', u'Accueil du public', u'Acidification du sol', ..., u'pH', u'test']

    >>> thesaurus.terms.get(u'Abri').generic is None
    True

    >>> thesaurus.terms.get(u'Abri').parent.label
    u'Abri'

    >>> thesaurus.terms.get(u'Eclaircie').parent.label
    u'Sylviculture'

    >>> sorted([term.label for term in thesaurus.terms.get(u'Couvert').specifics])
    []

So a given term can be linked directly to only one generic and zero or more specific terms, to create a hierarchy:

    >>> thesaurus.terms.get(u'Eclaircie').generic.label
    u'Soins aux jeunes peuplements'

    >>> sorted([term.label for term in thesaurus.terms.get(u'Soins aux jeunes peuplements').specifics])
    [u'D\xe9gagement de plantation', u'D\xe9gagement de semis', u'D\xe9pressage', u'D\xe9tourage',
    u'Eclaircie', u'Nettoiement']

It's then possible to get a term's parents ; result is ordered, from first to last parent:

    >>> [term.label for term in thesaurus.terms.get(u'Eclaircie').getParents()]
    [u'Soins aux jeunes peuplements', u'Sylviculture']

The "level" of a term is his depth in the hierarchy
    >>> thesaurus.terms.get(u'Eclaircie').level
    3

To get "brothers" of a term:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Soins aux jeunes peuplements').getParentChilds()])
    [u'Cloisonnement', u'Coupe', u"D\xe9signation d'arbres objectif", u'Elagage', u'Emondage', u'Martelage',
    u'Populiculture', u'Pr\xe9d\xe9signation', u'Pr\xe9paration de la station', u'Rec\xe9page',
    u'R\xe9g\xe9n\xe9ration', u"Sylviculture d'arbres", u'Sylviculture de rattrapage', u'Sylviculture douce',
    u'Sylviculture dynamique', u'Sylviculture intensive', u'Sylviculture traditionnelle', u'Taille de formation']

To get all childs of a term's generic:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Soins aux jeunes peuplements').generic.specifics])
    [u'Cloisonnement', u'Coupe', u"D\xe9signation d'arbres objectif", u'Elagage', u'Emondage', u'Martelage',
    u'Populiculture', u'Pr\xe9d\xe9signation', u'Pr\xe9paration de la station', u'Rec\xe9page',
    u'R\xe9g\xe9n\xe9ration', u'Soins aux jeunes peuplements', u"Sylviculture d'arbres", u'Sylviculture de rattrapage',
    u'Sylviculture douce', u'Sylviculture dynamique', u'Sylviculture intensive', u'Sylviculture traditionnelle',
    u'Taille de formation']

And to get the full sub-hierarchy of a given term:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Soins aux jeunes peuplements').getAllChilds()])
    [u'D\xe9gagement de plantation', u'D\xe9gagement de semis', u'D\xe9pressage', u'D\xe9pressage avec cloisonnement',
    u'D\xe9pressage syst\xe9matique', u'D\xe9tourage', u'Eclaircie', u'Eclaircie par le bas', u'Eclaircie par le haut',
    u'Eclaircie pr\xe9coce', u'Eclaircie sanitaire', u'Eclaircie syst\xe9matique', u'Eclaircie syst\xe9matique en ligne',
    u'Eclaircie s\xe9lective', u'Eclaircie s\xe9lective avec cloisonnement', u'Eclaircie tardive',
    u'Mise \xe0 distance', u'Nettoiement', u'Premi\xe8re \xe9claircie']

A term can also be linked to several synonyms, outside it's hierarchy or not:

    >>> sorted([term.label for term in thesaurus.terms.get(u'Base de loisir').used_for])
    [u'Base de plein air et de loisir']

The reciprocity can be verified:

    >>> thesaurus.terms.get(u'Base de plein air et de loisir').usage.label
    u'Base de loisir'

Finally, this kind of thesaurus can provide associations between words:

    >>> sorted([term.label for term in thesaurus.terms.get('Abri').associations])
    [u"Coupe d'abri", u'Couvert', u'Plantation sous abri', u'Rayonnement solaire']


Using thesaurus extracts
------------------------

A thesaurus can contain extracts, which are sub-sets of thesaurus terms. Each thesaurus term can then be associated with
zero or more extracts.

The main rule concercing the association between terms and extracts is that a term can be associated with an extract
only if it's generic term is also associated with it, and so recursively.

    >>> term = thesaurus.terms.get(u'Soins aux jeunes peuplements')
    >>> sorted([t.label for t in term.generic.specifics])
    [u'Cloisonnement', u'Coupe', u"D\xe9signation d'arbres objectif", u'Elagage', u'Emondage', u'Martelage',
    u'Populiculture', u'Pr\xe9d\xe9signation', u'Pr\xe9paration de la station', u'Rec\xe9page',
    u'R\xe9g\xe9n\xe9ration', u'Soins aux jeunes peuplements', u"Sylviculture d'arbres", u'Sylviculture de rattrapage',
    u'Sylviculture douce', u'Sylviculture dynamique', u'Sylviculture intensive', u'Sylviculture traditionnelle',
    u'Taille de formation']

    >>> term.extracts is None
    True

    >>> from ztfy.thesaurus.interfaces.thesaurus import IThesaurusExtracts
    >>> from ztfy.thesaurus.thesaurus import ThesaurusExtract
    >>> extract = ThesaurusExtract()
    >>> extract.name = u'Thesaurus extract'
    >>> IThesaurusExtracts(thesaurus)[extract.name] = extract

If we try to set an extract on a term randomly, we won't always get the good result:

    >>> term.extracts = set((extract.name,))
    >>> term.extracts is None
    True

Term extracts are still empty because term's generic is not associated to this extract.

    >>> term.generic.extracts = set((extract.name,))
    >>> term.extracts = set((extract.name,))
    >>> term.extracts
    set([u'Thesaurus extract'])

Of course, this works only because term's generic is a toplevel term.

Resetting a term's extracts afterwards also reset extracts of it's specific terms:

    >>> term.generic.extracts = set()
    >>> term.extracts
    set([])
