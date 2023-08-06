# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  Dean Gardiner <gardiner91@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyupnp.event import EventProperty
from pyupnp.services import Service, ServiceActionArgument,\
    register_action, ServiceStateVariable


class ContentDirectoryService(Service):
    version = (1, 0)
    serviceType = "urn:schemas-upnp-org:service:ContentDirectory:1"
    serviceId = "urn:upnp-org:serviceId:ContentDirectory"

    subscription_timeout_range = (None, None)

    actions = {
        'Browse': [
            ServiceActionArgument('ObjectID',           'in',   'A_ARG_TYPE_ObjectID'),
            ServiceActionArgument('BrowseFlag',         'in',   'A_ARG_TYPE_BrowseFlag'),
            ServiceActionArgument('Filter',             'in',   'A_ARG_TYPE_Filter'),
            ServiceActionArgument('StartingIndex',      'in',   'A_ARG_TYPE_Index'),
            ServiceActionArgument('RequestedCount',     'in',   'A_ARG_TYPE_Count'),
            ServiceActionArgument('SortCriteria',       'in',   'A_ARG_TYPE_SortCriteria'),

            ServiceActionArgument('Result',             'out',  'A_ARG_TYPE_Result'),
            ServiceActionArgument('NumberReturned',     'out',  'A_ARG_TYPE_Count'),
            ServiceActionArgument('TotalMatches',       'out',  'A_ARG_TYPE_Count'),
            ServiceActionArgument('UpdateID',           'out',  'A_ARG_TYPE_UpdateID'),
        ],
        'GetSearchCapabilities': [
            ServiceActionArgument('SearchCaps',         'out',  'SearchCapabilities'),
        ],
        'GetSortCapabilities': [
            ServiceActionArgument('SortCaps',           'out',  'SortCapabilities'),
        ],
        'GetSystemUpdateID': [
            ServiceActionArgument('Id',                 'out',  'SystemUpdateID'),
        ],
        'UpdateObject': [
            ServiceActionArgument('ObjectID',           'in',   'A_ARG_TYPE_ObjectID'),
            ServiceActionArgument('CurrentTagValue',    'in',   'A_ARG_TYPE_TagValueList'),
            ServiceActionArgument('NewTagValue',        'in',   'A_ARG_TYPE_TagValueList'),
        ],
        'Search': [
            ServiceActionArgument('ContainerID',        'in',   'A_ARG_TYPE_ObjectID'),
            ServiceActionArgument('SearchCriteria',     'in',   'A_ARG_TYPE_SearchCriteria'),
            ServiceActionArgument('Filter',             'in',   'A_ARG_TYPE_Filter'),
            ServiceActionArgument('StartingIndex',      'in',   'A_ARG_TYPE_Index'),
            ServiceActionArgument('RequestedCount',     'in',   'A_ARG_TYPE_Count'),
            ServiceActionArgument('SortCriteria',       'in',   'A_ARG_TYPE_SortCriteria'),

            ServiceActionArgument('Result',             'out',  'A_ARG_TYPE_Result'),
            ServiceActionArgument('NumberReturned',     'out',  'A_ARG_TYPE_Count'),
            ServiceActionArgument('TotalMatches',       'out',  'A_ARG_TYPE_Count'),
            ServiceActionArgument('UpdateID',           'out',  'A_ARG_TYPE_UpdateID'),
        ],
        'X_GetRemoteSharingStatus': [
            ServiceActionArgument('Status',             'out',  'X_RemoteSharingEnabled'),
        ],
    }
    stateVariables = [
        # Arguments
        ServiceStateVariable('A_ARG_TYPE_ObjectID',         'string'),
        ServiceStateVariable('A_ARG_TYPE_Result',           'string'),
        ServiceStateVariable('A_ARG_TYPE_SearchCriteria',   'string'),
        ServiceStateVariable('A_ARG_TYPE_BrowseFlag',       'string', [
            'BrowseMetadata', 'BrowseDirectChildren'
        ]),
        ServiceStateVariable('A_ARG_TYPE_Filter',           'string'),
        ServiceStateVariable('A_ARG_TYPE_SortCriteria',     'string'),
        ServiceStateVariable('A_ARG_TYPE_Index',            'ui4'),
        ServiceStateVariable('A_ARG_TYPE_Count',            'ui4'),
        ServiceStateVariable('A_ARG_TYPE_UpdateID',         'ui4'),
        ServiceStateVariable('A_ARG_TYPE_TagValueList',     'string'),

        # Variables
        ServiceStateVariable('SearchCapabilities',          'string'),
        ServiceStateVariable('SortCapabilities',            'string'),
        ServiceStateVariable('SystemUpdateID',              'ui4',
                             sendEvents=True),
        #ServiceStateVariable('ContainerUpdateIDs',          'string',
        #                     sendEvents=True),
        ServiceStateVariable('X_RemoteSharingEnabled',      'boolean',
                             sendEvents=True),
    ]

    system_update_id = EventProperty('SystemUpdateID')
    #container_update_ids = EventProperty('ContainerUpdateIDs')
    remote_sharing_enabled = EventProperty('X_RemoteSharingEnabled', 1)

    @register_action('Browse')
    def browse(self, objectID, browseFlag, browseFilter, startingIndex,
               requestedCount, sortCriteria):
        raise NotImplementedError()

    @register_action('GetSearchCapabilities')
    def getSearchCapabilities(self):
        raise NotImplementedError()

    @register_action('GetSortCapabilities')
    def getSortCapabilities(self):
        raise NotImplementedError()

    @register_action('GetSystemUpdateID')
    def getSystemUpdateID(self):
        raise NotImplementedError()

    @register_action('UpdateObject')
    def updateObject(self, objectID, currentTagValue, newTagValue):
        raise NotImplementedError()

    @register_action('Search')
    def search(self, containerID, searchCriteria, searchFilter, startingIndex,
               requestedCount, sortCriteria):
        raise NotImplementedError()

    @register_action('X_GetRemoteSharingStatus')
    def getRemoteSharingStatus(self):
        raise NotImplementedError()
