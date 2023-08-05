import transaction
import logging
import os

from types import DictType
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.WorkflowTool import WorkflowException

from zope.interface import alsoProvides
from zope.component import getUtility, queryUtility, getMultiAdapter

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.app.folder.folder import IATUnifiedFolder
from plone.portlets.interfaces import (
    IPortletAssignmentMapping,
    ILocalPortletAssignmentManager,
    IPortletManager
)

from plone.i18n.normalizer.interfaces import IURLNormalizer

LANGUAGE = 'en'
try:
    from Products import LinguaPlone
except ImportError:
    LANGUAGE = None


logger = logging.getLogger('Sitesetup tools:structure')


def _createItem(context, item, default_language=LANGUAGE, base_path=''):
    if not item.get('id') and item['title']:
        normalizer = queryUtility(IURLNormalizer)
        gen_id = normalizer.normalize(item['title'])
    elif not item.get('id') and not item['title']:
        raise 'Missing title or id'
    elif item.get('id'):
        gen_id = item['id']

    if gen_id not in context.objectIds():
        _createObjectByType(item['type'], context,
            id=gen_id,
            title=item['title'])

        obj = context[gen_id]
        obj.unmarkCreationFlag()

    else:
        obj = context[gen_id]

    logger.info('Created %s' % (repr(obj)))
    transition = item.get('transition')
    if transition:
        workflow = obj.portal_workflow
        try:
            workflow.doActionFor(obj, transition)
        except WorkflowException:
            ## No action - maybe the object is already in required state
            pass


    mark_ifs = item.get('interfaces')
    if mark_ifs:
        for mark_if in mark_ifs:
            alsoProvides(obj, mark_if)

    portlets = item.get('portlets')
    if portlets:
        """
        Example:
        1) pass module with Assignment class (it will work with right portlets only!)
        'portlets': [ plone.app.portlets.portlets.calendar ]
        2) pass dictionary with additional parameters
           Only 'module' is required
        'portlets': [ { 'module': plone.app.portlets.portlets.classic,
                        'name': 'myportlet1',
                        'manager': 'plone.rightcolumn',
                        'params': dict(template='mytemplate', macro='portlet')
                      } ]
        """
        for portlet in portlets:
            if isinstance(portlet, DictType):
                assert 'module' in portlet, 'Please provide portlet module'
                if 'name' not in portlet:
                    portlet['name'] = portlet['module'].__name__
                if 'params' not in portlet:
                    portlet['params'] = dict()
                if 'manager' not in portlet:
                    portlet['manager'] = u'plone.rightcolumn'
            else:
                portlet = {'module': portlet,
                           'name': portlet.__name__,
                           'manager': u'portlet.rightcolumn',
                           'params': dict(),
                          }
            col = getUtility(IPortletManager,
                             name = portlet['manager'])
            slot = getMultiAdapter((obj, col,),
                                    IPortletAssignmentMapping,
                                    context = obj)
            if portlet['name'] not in slot:
                portlet_obj = portlet['module'].Assignment(**portlet['params'])
                slot[portlet['name']] = portlet_obj


    block = item.get('block-portlets')
    if block is not None:
        if isinstance(block, DictType):
            assert 'block' in block, 'Please provide "block" parameter for block-portlets'
            if 'manager' not in block:
                block['manager'] = u'plone.rightcolumn'
        else:
            block = dict(
                            manager=u'plone.rightcolumn',
                            block=not not block
                        )
        col = getUtility(IPortletManager,
                              name = block['manager'])
        assignable = getMultiAdapter((obj, col), ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, block['block'])

    ## Local contrainst
    allowed_types = item.get('allowed_types')
    if allowed_types is not None:
        obj.setConstrainTypesMode(1)
        obj.setLocallyAllowedTypes(allowed_types)
        obj.setImmediatelyAddableTypes(allowed_types)

    ## Layout
    layout = item.get('layout')
    if layout is not None:
        obj.setLayout(layout)

    ## Default page
    default_page = item.get('default_page')
    if default_page is not None:
        obj.setDefaultPage(default_page)

    ## Navigation
    exclude = item.get('exclude_from_nav')
    if exclude:
        obj.setExcludeFromNav(True)

    # Image/File types
    if item['type'] == 'Image':
        field = obj.getField('image')
    elif item['type'] == 'File':
        field = obj.getField('file')
    else:
        field = None

    if field is not None:
        # unicode path would raise exception when viewing image on site, because
        # of the unicode filename
        path = str(os.path.join(base_path, item['file']))
        if os.path.isfile(path):
            # basename = os.path.split('/')[-1]
            # contenttype = guess_content_type(name=basename, body=value)
            fp = open(path, 'rb')
            field.set(obj, fp)
            fp.close()

    # reference
    reference = item.get('reference', '')
    if reference:
        for field, value in reference.items():
            field = obj.getField(field)
            if field is not None:
                portal = context.portal_url.getPortalObject()
                portal_id = portal.getId()
                if isinstance(value, str):
                    target = portal.unrestrictedTraverse(portal_id + value, None)
                    if target is None:
                        logger.warning("Unable to traverse to %s. Field %s of %s not set!" % (portal_id + value, field, obj))
                    else:
                        field.set(obj, target)
                elif isinstance(value, list):
                    targets = []
                    for v in value:
                        target = portal.unrestrictedTraverse(portal_id + v, None)
                        if target is None:
                            logger.warning("Unable to traverse to %s. Field %s of %s not set!" % (portal_id + v, field, obj))
                        else:
                            targets.append(target)
                    if targets:
                        field.set(obj, targets)

    # general field setup
    for k, v in item.items():
        if k.startswith('field_'):
            fieldname = k[6:]
            field = obj.getField(fieldname)
            if field is not None:
                field.set(obj, v)
            else:
                logger.warning('Field %s of %s does not exist.' % (fieldname, obj) )

    # We have linguaplone
    if LANGUAGE:
        language = item.get('language', '')
        translations = item.get('translations', {})

        if not language and not translations:
            obj.setLanguage(default_language)
            transaction.savepoint()
        else:
            if language:
                obj.setLanguage(language)
            else:
                obj.setLanguage(default_language)

            if translations:
                transaction.savepoint()
                for lang, data in translations.items():
                    if not obj.hasTranslation(lang):
                        obj.addTranslation(lang, **data)

    subfolder = item.get('subfolder')
    transaction.savepoint()

    # use this to remove default contents of the folderish object
    if item.get('remove_contents', 0):
        logger.info('Removing contents the created content: %s' % obj.title)
        if IATUnifiedFolder.providedBy(obj):
            obj.manage_delObjects([i for i in obj.objectIds()])

    if subfolder:
        for item in subfolder:
            _createItem(obj, item, default_language, base_path)

    obj.reindexObject()

def clearUpSite(context, to_delete):
    """ Remove content from the plone site root using given list of ids e.g.:
        TO_DELETE = ['news', 'events']
    """

    existing = context.objectIds()

    for item in to_delete:
        if item in existing:
            context.manage_delObjects([item,])

def setupStructure(portal, structure, default_language=LANGUAGE, base_path=''):
    """ Setup initial content structure. e.g.:

        STRUCTURE = [
            {
                'title' : 'About us',
                'type' : 'Document',
                'interfaces': (
                    IMyCustomMarkerInterface,
                )
            },
            {
                'title' : 'Products',
                'type' : 'Folder',
                'layout': 'folder_listing',
                'subfolder': [
                    {
                        'title': 'Cheap Products',
                        'type': 'Folder',
                        'allowed_type': ['Document'],
                        'subfolder': [
                            {
                                'title': 'Product 1',
                                'type': 'Document',
                                'layout': '@@product-page'
                            },
                            {
                                'title': 'Recommended',
                                'type': 'Collection',
                            }
                        ]
                    }
                ]
            }
        ]
    """
    for item in structure:
        _createItem(portal, item, default_language=default_language, base_path=base_path)