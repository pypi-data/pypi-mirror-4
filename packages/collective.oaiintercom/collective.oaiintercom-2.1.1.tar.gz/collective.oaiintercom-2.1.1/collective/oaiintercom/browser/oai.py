# -*- coding: us-ascii -*-
# _______________________________________________________________________
#              __________                      .__        
#   ____   ____\______   \____________  ___  __|__| ______
# _/ __ \ /    \|     ___/\_  __ \__  \ \  \/  /  |/  ___/
# \  ___/|   |  \    |     |  | \// __ \_>    <|  |\___ \ 
#  \___  >___|  /____|     |__|  (____  /__/\_ \__/____  >
#      \/     \/                      \/      \/       \/ 
# _______________________________________________________________________
# 
#    This file is part of the eduCommons software package.
#
#    Copyright (c) 2012 enPraxis, LLC
#    http://enpraxis.net
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2.8  
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
# _______________________________________________________________________

__author__ = 'Brent Lambert <brent@enpraxis.net>'


from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from urlparse import urlparse
from DateTime import DateTime
from oaierror import *


class OAIProvider(BrowserView):
    """ View class for OAI feeds """

    # Templates for OAI response output in XML

    render_error = ViewPageTemplateFile('oaierror.pt')
    render_identify = ViewPageTemplateFile('oaiidentify.pt')
    render_listmetadataformats = ViewPageTemplateFile('oailistmetadataformats.pt')
    render_listsets = ViewPageTemplateFile('oailistsets.pt')
    render_listidentifiers = ViewPageTemplateFile('oailistidentifiers.pt')
    render_listrecords = ViewPageTemplateFile('oailistrecords.pt')
    render_getrecord = ViewPageTemplateFile('oaigetrecord.pt')

    def __call__(self):
        self.request.response.setHeader('ContentType',
                                        'text/xml;; charset=utf-8')
        self.request.response.setHeader('charset', 'UTF-8')
        if self.request.has_key('verb'):
            if 'Identify' == self.request['verb']:
                try:
                    self._getIdentify()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_identify()
            elif 'ListMetadataFormats' == self.request['verb']:
                try:
                    self._getListMetadataFormats()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_listmetadataformats()
            elif 'ListSets' == self.request['verb']:
                try:
                    self._getListSets()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_listsets()
            elif 'ListIdentifiers' == self.request['verb']:
                try:
                    self._getListIdentifiers()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_listidentifiers()
            elif 'ListRecords' == self.request['verb']:
                try:
                    self._getListRecords()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_listrecords()
            elif 'GetRecord' == self.request['verb']:
                try:
                    self._getGetRecord()
                except OAIError, e:
                    return self._getError(e.code, e.desc)
                return self.render_getrecord()
            else:
                errmsg = em_illegalverb %self.request['verb']
                self.request['verb'] = None
                return self._getError(e_badverb, errmsg)
        return self._getError(e_badverb, em_verbmissing)

    def _getError(self, code, desc):
        """ Return an OAI error """
        self.request['oaierrcode'] = code
        self.request['oaierrdesc'] = desc
        return self.render_error()

    def _getIdentify(self):
        """ Get OAI Identify response data """
        self._checkParams(['verb'])
        self.request['oaiid'] = self._getOID()
        self.request['domain'] = self.request['oaiid'].split(':')[-1]

    def _getListMetadataFormats(self):
        """ Get list of supported metadata formats """
        self._checkParams(['verb', 
                           'identifier'])
        if self.request.has_key('identifier'):
            self._getIdentifier()
        
    def _getListSets(self):
        """ Get list of sets in the site """
        self._checkParams(['verb', 
                           'resumptionToken'])
        if self.request.has_key('resumptionToken'):
            raise OAIError(e_badrestoken, em_restokmissing)
        self.request['oaiid'] = self._getOID()
        catalog = getToolByName(self.context, 'portal_catalog')
        properties = getToolByName(self.context, 'portal_properties')
        oaiprops = properties.oaiintercom_properties
        stypes = oaiprops.getProperty('provideMetadataFor')
        results = catalog.searchResults(is_folderish=True,
                                        portal_type=stypes)
        if not results:
            raise OAIError(e_nosethierarchy, em_noresults)
        self.request['searchresults'] = results
    
    def _getListIdentifiers(self):
        """ Get list of identifiers """
        # Check parameters
        self._checkParams(['verb', 
                           'from', 
                           'until', 
                           'metadataPrefix',
                           'set',
                           'resumptionToken'])
        if self.request.has_key('resumptionToken'):
            raise OAIError(e_badrestoken, em_restokmissing)
        if not self.request.has_key('metadataPrefix'):
            raise OAIError(e_badarg, em_mdprefixmissing)
        if self.request['metadataPrefix'] != 'oai_dc':
            raise OAIError(e_cannotdissformat, em_badmdprefix %self.request['metadataPrefix'])
        # Get search results
        self.request['portalid'] = self.context.portal_url.getPortalObject().id
        self._getSearchResults()

    def _getListRecords(self):
        """ Get list of records in the site """
        # Check parameters
        self._checkParams(['verb', 
                           'from', 
                           'until', 
                           'set',
                           'resumptionToken',
                           'metadataPrefix'])
        if self.request.has_key('resumptionToken'):
            raise OAIError(e_badrestoken, em_restokmissing)
        if not self.request.has_key('metadataPrefix'):
            raise OAIError(e_badarg, em_mdprefixmissing)
        if self.request['metadataPrefix'] != 'oai_dc':
            raise OAIError(e_cannotdissformat, em_badmdprefix %self.request['metadataPrefix'])
        # Get search results
        self.request['portalid'] = self.context.portal_url.getPortalObject().id
        self._getSearchResults()

    def _getGetRecord(self):
        """ Get record information based on identifier """
        self._checkParams(['verb', 
                           'identifier', 
                           'metadataPrefix'])
        if not self.request.has_key('metadataPrefix'):
            raise OAIError(e_badarg, em_mdprefixmissing)
        if self.request['metadataPrefix'] != 'oai_dc':
            raise OAIError(e_cannotdissformat, em_badmdprefix %self.request['metadataPrefix'])
        if not self.request.has_key('identifier'):
            raise OAIError(e_badarg, em_identmissing)
        self._getIdentifier()
        
    # Request helper functions

    def _checkParams(self, params):
        """ Check for illegal parameters """
        for x in self.request.form.keys():
            if x not in params:
                raise OAIError(e_badarg, em_illegalparam % x)

    def _getIdentifier(self):
        """ Get the brains for an object in the ZODB """
        if self.request.has_key('identifier'):
            catalog = getToolByName(self.context, 'portal_catalog')
            properties = getToolByName(self.context, 'portal_properties')
            self.request['oaiid'] = self._getOID()
            self.request['portalid'] = self.context.portal_url.getPortalObject().id
            path = self.oai2zodb(self.request['identifier'])
            oaiprops = properties.oaiintercom_properties
            stypes = oaiprops.getProperty('provideMetadataFor')
            results = catalog.searchResults(path={'query':path, 
                                                  'depth':0},
                                            portal_type=stypes)
            if not results:
                raise OAIError(e_idnotexist, 
                               em_idnotinrepository %self.request['identifier'])
            self.request['searchresults'] = results
        

    def _getOID(self):
        domain = urlparse(self.request.getURL())[1]
        return 'oai:%s' %domain.split(':')[0]

    def _getSearchResults(self):
        """ Get set of brains based on search parameters """
        # Get search results
        self.request['oaiid'] = self._getOID()
        self.request['portalid'] = self.context.portal_url.getPortalObject().id
        catalog = getToolByName(self.context, 'portal_catalog')
        properties = getToolByName(self.context, 'portal_properties')
        oaiprops = properties.oaiintercom_properties
        if self.request.has_key('set'):
            path = self.setspec2zodb(self.request['set'])
        else:
            path = '/' + self.request['portalid']
        if self.request.has_key('from'):
            fromd = DateTime(self.request['from'])
        else:
            edate = self.getEarliestDateStamp()
            if edate:
                fromd = DateTime(edate)
            else:
                raise OAIError(e_norecmatch, em_noresults)
        if self.request.has_key('until'):
            untild = DateTime(self.request['until'])
        else:
            untild = DateTime(self.getCurrentDateTime())
        if fromd > untild:
            raise OAIError(e_badarg, em_datemismatch)
        stypes = oaiprops.getProperty('provideMetadataFor')
        results = catalog.searchResults(
            path={'query':path},
            Date={'query':[fromd,untild+1], 'range':'min:max',},
            portal_type=stypes)
        if not results:
            raise OAIError(e_norecmatch, em_noresults)
        self.request['searchresults'] = results

    # View class helper functions

    def oai2zodb(self, id):
        """ Convert OAI ID to ZODB path """
        path = id.split(':')
        if len(path) < 3 or ':'.join(path[:2]) != self.request['oaiid']:
            raise OAIError(e_badarg, em_invalidident %id)
        return '/%s/%s' %(self.request['portalid'],
                          '/'.join(path[2:]))

    def zodb2oai(self, id):
        """ Convert ZODB path to OAI ID """
        oid = id.split('/')[2:]
        return '%s:%s' %(self.request['oaiid'],
                          '/'.join(oid))

    def zodb2setspec(self, path):
        """ Convert ZODB path to OAI setSpec """
        sspec = path.split('/')[2:]
        return ':'.join(sspec)

    def setspec2zodb(self, sspec):
        """ Convert setSpec to ZODB path """
        path = sspec.split(':')
        return '/%s/%s' %(self.request['portalid'], '/'.join(path))

    def getCurrentDateTime(self):
        """ Returns the current date in correct format """
        return DateTime().toZone('GMT+0').strftime('%Y-%m-%dT%H:%M:%SZ')

    def getEarliestDateStamp(self):
        """ Return the earliest date stamp for all content """
        catalog = getToolByName(self.context, 'portal_catalog')
        properties = getToolByName(self.context, 'portal_properties')
        oaiprops = properties.oaiintercom_properties
        stypes = oaiprops.getProperty('provideMetadataFor')
        results = catalog.searchResults(sort_on='Date',
                                        sort_order='ascending',
                                        sort_limit=1,
                                        portal_type=stypes)
        if results:
            return self.formatDate(results[0].Date)
        return None
        
    def formatDate(self, date):
        """ Format the date for OAI """
        fdate = DateTime(date).toZone('GMT+0')
        return fdate.strftime('%Y-%m-%d')

    def getParentObject(self, path):
        """ Get parent object from brain path and return as 
        setSpec """
        sspec = path.split('/')[2:]
        if len(sspec) > 2:
            return ':'.join(sspec[:-1])
        return None
            
        
