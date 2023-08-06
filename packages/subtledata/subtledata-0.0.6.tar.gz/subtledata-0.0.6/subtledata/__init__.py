"""
Subtledata Python Client Library

AUTHOR

George Sibble
Chief Software Architect
Subtledata, Inc.
george.sibble@subtledata.com
Github:  sibblegp


************TO USE************

LICENSE (The MIT License)

Copyright (c) 2013 Subtledata, Inc. "code@subtledata.com"

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

__author__ = 'gsibble'

import config
import json

from api import swagger

from api.LocationsApi import LocationsApi
from api.UsersApi import UsersApi
from api.TicketsApi import TicketsApi

import exceptions as E


class SDFirstClassObject(object):
    def __init__(self, api_client, use_cache=True, *args, **kwargs):
        self._api_key = api_client.apiKey
        self._api_client = api_client
        self._use_cache = use_cache
        self._swagger_locations_api = LocationsApi(self._api_client)
        self._swagger_users_api = UsersApi(self._api_client)
        self._swagger_tickets_api = TicketsApi(self._api_client)


class SDLocation(SDFirstClassObject):
    class SDMenu(object):

        def __init__(self, swagger_menu):

            #Set up the public lists
            self.items = []
            self.categories = swagger_menu

            #Set up the private item dictionaries
            self._item_name_dict = {}
            self._item_id_dict = {}

            #Set up private category dictionaries
            self._category_name_dict = {}
            self._category_id_dict = {}

            for category in swagger_menu:
                self._category_name_dict[category.category_name] = category
                self._category_id_dict[category.category_id] = category

                #Store the items
                for item in category.items:
                    setattr(item, 'category', category.category_name)
                    self.items.append(item)
                    self._item_name_dict[item.name] = item
                    self._item_id_dict[item.item_id] = item

        def get_category(self, category_id=None, category_name=None):

            category_object = None

            if category_id is not None:
                category_object = self._category_id_dict[category_id]
            elif category_name is not None:
                category_object = self._category_name_dict[category_name]

            return category_object

        def get_item(self, item_id=None, item_name=None):

            item_object = None

            if item_id is not None:
                item_object = self._item_id_dict[item_id]
            elif item_name is not None:
                item_object = self._category_name_dict[item_name]

            return item_object

    class SDTable(object):

        def __init__(self, swagger_table, parent):

            self._swagger_locations_api = parent._swagger_locations_api
            self._swagger_ticket_api = parent._swagger_tickets_api
            self._api_key = parent._api_client.apiKey
            self._swagger_table = swagger_table
            self._location_id = parent.location_id
            self._api_client = parent._api_client
            for attribute in self._swagger_table.swaggerTypes:
                self.__setattr__(attribute, getattr(self._swagger_table, attribute))

        def open_ticket(self, user_id, device_id, number_of_people_in_party=1, business_expense=False, custom_ticket_name=None, return_ticket_details=False):

            if hasattr(self, 'revenue_center_id') and hasattr(self, 'subtledata_id'):
                ticket_body = {
                    "revenue_center_id": self.revenue_center_id,
                    "number_of_people_in_party": number_of_people_in_party,
                    "user_id": user_id,
                    "device_id": device_id,
                    "table_id": self.subtledata_id,
                    "business_expense": business_expense,
                    "custom_ticket_name": custom_ticket_name
                }
            else:
                raise KeyError('Table missing key data')

            print ticket_body

            #Send the request
            ticket_response = self._swagger_locations_api.createTicket(self._location_id, self._api_key, ticket_type='dine-in', body=ticket_body)

            print ticket_response.ticket_id

            if return_ticket_details:
                #Get the totals
                return SDTicket(self._api_client, ticket_response.ticket_id, user_id)

            else:
                return SDTicket(self._api_client, ticket_response.ticket_id, user_id)


    def __init__(self, location_id, api_client, include_menu, use_cache, *args, **kwargs):
        super(SDLocation, self).__init__(api_client, use_cache)
        self._location_id = location_id

        #Get the location via swagger
        self._swagger_location = self._swagger_locations_api.getLocation(location_id, self._api_key,
                                                                        use_cache=self._use_cache)

        #Set attributes of first class Location to match Swagger Location object
        for attribute in self._swagger_location.swaggerTypes:
            self.__setattr__(attribute, getattr(self._swagger_location, attribute))

        #Set the tables to be our type
        self.tables = [SDLocation.SDTable(table, self) for table in self.tables]

        if include_menu:
            self.update_menu(use_cache)

    def update_menu(self, use_cache=True):

        if not self._use_cache:
            use_cache = False

        self._swagger_menu = self._swagger_locations_api.getLocationMenu(self._location_id, self._api_key,
                                                                        use_cache=use_cache)

    @property
    def menu(self):

        if not hasattr(self, '_swagger_menu'):
            self.update_menu()

        return self.SDMenu(self._swagger_menu)

    def open_ticket_for_dine_in(self, user_id, device_id, table_id, business_expense=False):
        new_ticket_body = {

        }

        #TODO:  Implement Later
        #Return a SDTicket
        pass

    def open_ticket_for_take_out(self, user_id):

        #Return a SDTicket
        pass

    def open_ticket_for_delivery(self, user_id):

        #Return a SDTicket
        pass


class SDUser(SDFirstClassObject):
    def __init__(self, api_client, user_id=False, user_name=None, use_cache=True, *args, **kwargs):
        super(SDUser, self).__init__(api_client, use_cache)

        if user_id is not None:
            self._swagger_user = self._swagger_users_api.getUser(user_id, self._api_key, use_cache=self._use_cache)
        elif user_name is not None:
            self._swagger_user = self._swagger_users_api.searchUsersByName(user_name, self._api_key,
                                                                           use_cache=self._use_cache)
        else:
            self._swagger_user = None

        if self._swagger_user is not None:
            for attribute in self._swagger_user.swaggerTypes:
                self.__setattr__(attribute, getattr(self._swagger_user, attribute))

    def update_info(self):
        pass


class SDTicket(SDFirstClassObject):
    def __init__(self, api_client, ticket_id, user_id=None, get_values=True, *args, **kwargs):
        super(SDTicket, self).__init__(api_client, False)

        self.ticket_id = ticket_id
        self.user_id = user_id

        if get_values == True:
            pass
            #TODO:  Implement this
            # self._swagger_ticket = self._swagger_tickets_api.getTicket(ticket_id, user_id)
            #
            # if self._swagger_ticket is not None:
            #     for attribute in self._swagger_ticket.swaggerTypes:
            #         self.__setattr__(attribute, getattr(self._swagger_ticket, attribute))

    def add_item_to_order(self, item_id, quantity, instructions=None, modifiers=None):

        if hasattr(self, 'user_id') and hasattr(self, 'ticket_id'):
            if self.user_id is not None and self.ticket_id is not None:
                post_body = {
                    'item_id': int(item_id),
                    'quantity': quantity,

                }

                if instructions is not None:
                    post_body['instructions'] = instructions

                if modifiers is not None:
                    post_body['modifiers'] = modifiers

                print post_body

                returned_status = self._swagger_tickets_api.addItemsToOrder(self.ticket_id, self.user_id, self._api_key,
                                                                            body=post_body)

                return returned_status

            else:

                raise E.NoUserSetOnTicket
        else:
            raise E.NoUserSetOnTicket

    def submit_order(self):

        if hasattr(self, 'user_id') and hasattr(self, 'ticket_id'):
            if self.user_id is not None and self.ticket_id is not None:

                returned_status = self._swagger_tickets_api.submitOrder(self.ticket_id, self.user_id, self._api_key,
                                                                        body={'send': True})

                return returned_status
            else:
                raise E.NoUserSetOnTicket
        else:
            raise E.NoUserSetOnTicket


class SubtleData(object):
    class _SDFirstClassCollection(object):

        def __init__(self, parent, *args, **kwargs):
            self._api_key = parent.api_key
            self._use_cache = parent._use_cache
            self._api_client = parent._api_client

    class SDLocationCollection(_SDFirstClassCollection):

        def __init__(self, parent):
            super(SubtleData.SDLocationCollection, self).__init__(parent)

        def create(self):
            pass

        def get(self, location_id, use_cache=True, include_menu=False):
            if not self._use_cache:
                use_cache = False

            return SDLocation(location_id, self._api_client, include_menu, use_cache)

    class SDUserCollection(_SDFirstClassCollection):

        def __init__(self, parent):
            super(SubtleData.SDUserCollection, self).__init__(parent)

        def create(self):
            pass

        def get(self, user_id, use_cache=True):
            if not self._use_cache:
                use_cache = False

            return SDUser(self._api_client, user_id=user_id, use_cache=use_cache)

        def get_with_name(self, user_name, use_cache=True):
            if not self._use_cache:
                use_cache = False

            return SDUser(self._api_client, user_name=user_name, use_cache=use_cache)

    class SDTicketCollection(_SDFirstClassCollection):

        def __init__(self, parent):
            super(SubtleData.SDTicketCollection, self).__init__(parent)

        def get(self, ticket_id, user_id=None):
            return SDTicket(self._api_client, ticket_id=ticket_id, user_id=user_id)

        def get_with_pos_id(self, pos_id):
            pass

    def __init__(self, api_key, use_cache=True, testing=False, internal_debug=True):
        self.api_key = api_key
        self._use_cache = use_cache
        self._internal_debug = internal_debug

        if not testing:
            self._api_client = swagger.ApiClient(api_key, config.SD_ENDPOINT)
        else:
            self._api_client = swagger.ApiClient(api_key, config.SD_TESTING_ENDPOINT)

        self.Locations = SubtleData.SDLocationCollection(self)
        self.Users = SubtleData.SDTicketCollection(self)
        self.Tickets = SubtleData.SDTicketCollection(self)
