from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IText, IBool, ITextLine

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName

from jalon.primo.interfaces.utility import IPrimoLayout

class PrimoSettings(XMLAdapterBase):

    name = "primo"

    _LOGGER_ID = "portal_primo"

    attributes = {
        "layout": {
            "url_connexion" : {'type' : 'Text', 'default' : "http://domainname.com/exist/xmlrpc"},
            "url_catalogue" : {'type' : 'Text', 'default' : "http://domainname.com/exist/xmlrpc"},
            "url_acquisition" : {'type' : 'Text', 'default' : "http://domainname.com/exist/xmlrpc"},
            "login" : {'type' : 'Text', 'default' : u'admin'},
            "password" : {'type' : 'Text', 'default' : u'admin'},
        }
    }

    def _exportNode(self):
        """Export the object as a DOM node"""

        object = self._doc.createElement('object')

        # Loop through categories
        for key in self.attributes.keys():
            category = self.attributes[key]
            categorynode = self._doc.createElement(key)

            # Loop through fields in category
            for field in category.keys():
                fieldnode = self._doc.createElement(field)
                fieldvalue = getattr(self.context, field)

                if category[field]['type'] == 'Bool':
                    fieldnode.setAttribute('value', unicode(bool(fieldvalue)))
                elif category[field]['type'] == 'Text':

                    # Check for NoneType
                    if fieldvalue:
                        fieldnode.setAttribute('value', fieldvalue)
                    else:
                        fieldnode.setAttribute('value', '')
                elif category[field]['type'] == 'List':
                    if not fieldvalue:
                        fieldnode.setAttribute('value', '')
                    else:
                        for value in fieldvalue.split('\n'):
                            if value:
                                child = self._doc.createElement('element')
                                child.setAttribute('value', value)
                                fieldnode.appendChild(child)
                categorynode.appendChild(fieldnode)
            object.appendChild(categorynode)
        return object

    def _importNode(self, node):
        """Import the object from the DOM node"""
        if self.environ.shouldPurge() or node.getAttribute("purge").lower() == 'true':
            self._purgeAttributes()

        for categorynode in node.childNodes:
            if categorynode.nodeName != '#text' and categorynode.nodeName != '#comment':
                for fieldnode in categorynode.childNodes:
                    if fieldnode.nodeName != '#text' and fieldnode.nodeName != '#comment':
                        if self.attributes[categorynode.nodeName][fieldnode.nodeName]['type'] == 'Bool':
                            if fieldnode.hasAttribute('value'):
                                setattr(self.context, fieldnode.nodeName, self._convertToBoolean(fieldnode.getAttribute('value')))
                        elif self.attributes[categorynode.nodeName][fieldnode.nodeName]['type'] == 'Text':
                            if fieldnode.hasAttribute('value'):
                                setattr(self.context, fieldnode.nodeName, fieldnode.getAttribute('value'))
                        elif self.attributes[categorynode.nodeName][fieldnode.nodeName]['type'] == 'List':
                            field = getattr(self.context, fieldnode.nodeName)
                            if field is None or fieldnode.getAttribute("purge").lower() == 'true':
                                items = []
                            else:
                                items = field.split('\n')
                            for element in fieldnode.childNodes:
                                if element.nodeName != '#text' and element.nodeName != '#comment':
                                    if element.getAttribute('value') not in items:
                                        items.append(element.getAttribute('value'))
                            string = '\n'.join(items)
                            setattr(self.context, fieldnode.nodeName, string.decode())
        self._logger.info('Primo Settings imported.')

    def _purgeAttributes(self):
        """Purge current attributes"""

        # Loop through categories
        for key in self.attributes.keys():
            category = self.attributes[key]

            # Loop through fields in category
            for field in category.keys():
                fieldvalue = getattr(self.context, field)
                setattr(self.context, field, category[field]['default'])

def importPrimoSettings(context):
    """Import Primo Settings"""
    site = context.getSite()
    tool = getToolByName(site, 'portal_primo', None)
    if tool is None:
        return

    importObjects(tool, '', context)

def exportPrimoSettings(context):
    """Export Primo Settings"""
    site = context.getSite()
    tool = getToolByName(site, 'portal_primo', None)
    if tool is None:
        return

    exportObjects(tool, '', context)
