import os.path

import transaction

from App.Common import package_home
from StringIO import StringIO

from Products.Archetypes.atapi import listTypes
from Products.CMFCore.utils import getToolByName

from slc.seminarportal.config import DEPENDENCIES, PROJECTNAME
from slc.seminarportal.config import ADDITIONAL_CATALOG_INDEXES
from slc.seminarportal.config import product_globals as GLOBALS


def isNotSeminarPortalProfile(context):
    return context.readDataFile("seminarportal_marker.txt") is None


def installProductDependencies(context):
    if isNotSeminarPortalProfile(context):
        return
    out = StringIO()
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if not qi.isProductInstalled(product):
            print >> out, "Installing dependency %s:" % product
            qi.installProduct(product)
            transaction.savepoint(optimistic=True)
    transaction.commit()


def installAdditionalCatalogIndexes(context):
    if isNotSeminarPortalProfile(context):
        return

    try:
        import Products.QueueCatalog
    except ImportError:
        HAS_QUEUECATALOG = False
    else:
        HAS_QUEUECATALOG = True

    if HAS_QUEUECATALOG:
        # This step borks everything if QueueCatalog is installed.
        return

    indexes = []
    site = context.getSite()
    catalogTool = getToolByName(site, 'portal_catalog')
    for indexName, indexType in ADDITIONAL_CATALOG_INDEXES:
        indexes.append(indexName)
        if indexName not in catalogTool.indexes():
            catalogTool.addIndex(indexName, indexType)

    FSDTypes = [t['meta_type'] for t in listTypes(PROJECTNAME)]
    for brain in catalogTool(portal_type=FSDTypes):
        try:
            brain.getObject().reindexObject(indexes)
        except KeyError:
            # Relations content objects seem to not be able to handle
            # getObject(), but the data doesn't seem to get lost, so just
            # ignore it.
            pass


def installRelationsRulesets(context):
    if isNotSeminarPortalProfile(context):
        return

    site = context.getSite()
    relations_tool = getToolByName(site, 'relations_library', None)
    if relations_tool is None:
        return

    xmlpath = os.path.join(package_home(GLOBALS), 'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)
