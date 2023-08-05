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

from collective.oaiintercom import OAIIntercomMessageFactory as _

# Error codes

e_badverb = 'badVerb'
e_badarg = 'badArgument'
e_badrestoken = 'badResumptionToken'
e_cannotdissformat = 'cannotDisseminateFormat'
e_idnotexist = 'idDoesNotExist'
e_norecmatch = 'noRecordsMatch'
e_nomdformats = 'noMetadataFormats'
e_nosethierarchy = 'noSetHierarchy'

# Error Messages

em_verbmissing = _(u'The verb argument is missing or not supported')
em_illegalverb = _(u'The verb argument "%s" is not a legal OAI-PMH verb')
em_identmissing = _(u'The "identifier" argument is missing')
em_mdprefixmissing = _(u'The "metadataPrefix" argument is missing')
em_badmdprefix = _(u'The metadataPrefix argument "%s" is not supported by the repository')
em_restoknotsupp = _(u'Resumption tokens not supported by this repostiory.')
em_illegalparam = _(u'Parameter "%s" is illegal/not supported')
em_invalidident = _(u'Identifier "%s" is not in correct format')
em_noresults = _(u'No results found')
em_datemismatch = _(u'Date range error')
em_idnotinrepository = _(u'ID "%s" is not located in the repository')


class OAIError(Exception):
    """ Exception class for OAI errors """
    
    def __init__(self, code, desc):
        self.code = code
        self.desc = desc

    def __str__(self):
        return '%s: %s' %(self.code, self.desc)


