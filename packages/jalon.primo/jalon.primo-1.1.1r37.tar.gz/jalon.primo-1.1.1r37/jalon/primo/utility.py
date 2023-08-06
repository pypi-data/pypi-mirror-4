# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.primo.interfaces.utility import IPrimo, IPrimoLayout
from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel


from OFS.SimpleItem import SimpleItem

# Imports
import re
import urllib
import urllib2
import sys
from elementtree import ElementTree as ET


def form_adapter(context):
    """Form Adapter"""
    return getUtility(IPrimo)


class Primo(SimpleItem):
        """Primo Utility"""
        implements(IPrimo)
        classProvides(IPrimoLayout,)

        security = ClassSecurityInfo()
        url_connexion = FieldProperty(IPrimoLayout['url_connexion'])
        url_catalogue = FieldProperty(IPrimoLayout['url_catalogue'])
        url_acquisition = FieldProperty(IPrimoLayout['url_acquisition'])
        login = FieldProperty(IPrimoLayout['login'])
        password = FieldProperty(IPrimoLayout['password'])

        security.declarePrivate('requete')

        def requete(self, webservice, params, xpath=None):
            data = urllib.urlencode(params)
            url_connexion = self.url_connexion
            url_catalogue = self.url_catalogue
            if url_connexion.endswith("/"):
                url_connexion = url_connexion[:-1]
            req = urllib2.Request("%s/%s?%s" % (url_connexion, webservice, data))
            try:
                handle = urllib2.urlopen(req)
                rep = handle.read()
                try:
                    xml = ET.XML(rep)
                except:
                    # Erreur XML
                    return {"response": None, "error": sys.exc_info()}
            except:
                return req
            listeRES = []

            # a mettre en config admin
            listeNameSpace = ["{http://www.exlibrisgroup.com/xsd/primo/primo_nm_bib}", "{http://www.exlibrisgroup.com/xsd/jaguar/search}"]

            res = self.xpath(xml, "{1}JAGROOT/{1}RESULT/{1}DOCSET/{1}DOC".format(*listeNameSpace))
            if res:
                for record in res:
                    recordid = str(record.findtext("{0}PrimoNMBib/{0}record/{0}control/{0}recordid".format(*listeNameSpace)))
                    dico = {"type": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}type".format(*listeNameSpace)),
                            "title": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}title".format(*listeNameSpace)),
                            "creator": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}creator".format(*listeNameSpace)),
                            "publisher": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}publisher".format(*listeNameSpace)),
                            "creationdate": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}creationdate".format(*listeNameSpace)),
                            "format": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}format".format(*listeNameSpace)),
                            "recordid": recordid,  #identifiant document
                            "language": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}language".format(*listeNameSpace)),
                            "subject": [],
                            "image": [],
                            "urlcatalogue": "".join([url_catalogue, "/primo_library/libweb/action/display.do?tabs=detailsTab&ct=display&fn=search&doc=", recordid, "&indx=1&recIds=", recordid, "&recIdxs=0&elementId=0&renderMode=poppedOut&displayMode=full&frbrVersion=&dscnt=1&vl%2814793452UI1%29=all_items&scp.scps=&frbg=&tab=default_tab&srt=rank&mode=Basic&dum=true&vl%289521613UI0%29=any&vid=", self.getGenerique("etablissement")])
                            }
                    for subject in record.findall("{0}PrimoNMBib/{0}record/{0}display/{0}subject".format(*listeNameSpace)):
                        dico["subject"].append(subject.text)

                    for image in record.findall("{1}LINKS/{1}thumbnail".format(*listeNameSpace)):
                        dico["image"].append(image.text)

                    listeRES.append(dico)
            return listeRES

        security.declarePrivate('xpath')

        def xpath(self, xml, xpath):
            xpaths = xpath.split('/')
            xpathparent = '/'.join(xpaths[0:-1])
            if re.match(r"^@.*$", xpaths[-1]):
                parents = xml.findall(xpathparent)
                if len(parents) > 0:
                    key = xpaths[-1][1:]
                    if key in parents[0].attrib:
                        return parents[0].attrib[key]
            elif xpaths[-1] == "text()":
                parents = xml.findall(xpathparent)
                if len(parents) > 0:
                    return parents[0].text
            elif re.match(r"^\[.*\]", xpaths[-1]):
                parents = xml.findall(xpathparent)
                if len(parents) > 0:
                    return parents[int(xpaths[-1][1:-1])]
            else:
                return xml.findall(xpath)
            return None

        #plus d'info concernant un element
        def rechercherCatalogueBU(self, termeRecherche):
            params = {"institution": self.getGenerique("etablissement"),
                        "onCampus": "false",
                        "query": "any,contains,%s" % termeRecherche,
                        "indx": "1",
                        "bulkSize": "10",
                        "dym": "true",
                        "lang": "fre"
                        }
            return self.requete("search/brief", params)

        #renvoi sur le site de la BU
        def BUResult(self, termeRecherche):
            url_recherche = "".join([self.url_catalogue, "/primo_library/libweb/action/search.do?dscnt=0&vl%2814793452UI1%29=all_items&frbg=&scp.scps=&tab=default_tab&srt=rank&ct=search&mode=Basic&dum=true&indx=1&vl%289521613UI0%29=any&vl%28freeText0%29=", termeRecherche, "&fn=search&vid=", self.getGenerique("etablissement")])
            return url_recherche

        #Suggestions d’acquisitions
        def BUacquisition(self):
            url_acquisition = self.url_acquisition
            return url_acquisition

        def rechercherRecordById(self, recordid):
            params = {"institution": self.getGenerique("etablissement"),
                        "onCampus": "false",
                        "query": "rid,contains,%s" % recordid,
                        "indx": "1",
                        "bulkSize": "10",
                        "dym": "true",
                        "lang": "fre"}
            resultat = self.requete("search/brief", params)
            if resultat:
                return resultat[0]
            return None

        #recupére differents éléments génériques defini par l'administrateur dans les configs Jalon
        def getGenerique(self, generique):
            portal = self.portal_url.getPortalObject()
            jalon_conf = IJalonConfigurationControlPanel(portal)
            if generique == "etablissement":
                return jalon_conf.get_etablissement()
            else:
                return ""
