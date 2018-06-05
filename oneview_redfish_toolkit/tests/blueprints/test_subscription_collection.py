# -*- coding: utf-8 -*-

# Copyright (2017) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Python libs
import json
from unittest import mock

# 3rd party libs
from flask import Flask
from flask import Response
from flask_api import status

# Module libs
from oneview_redfish_toolkit.api.redfish_error import RedfishError
from oneview_redfish_toolkit.blueprints.subscription_collection\
    import subscription_collection
from oneview_redfish_toolkit.tests.base_test import BaseTest


class TestSubscriptionCollection(BaseTest):
    """Tests for SubscriptionCollection blueprint"""

    def setUp(self):
        """Tests SubscriptionCollection blueprint setup"""

        # creates a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(subscription_collection)

        @self.app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
        def internal_server_error(error):
            """General InternalServerError handler for the app"""

            redfish_error = RedfishError(
                "InternalError",
                "The request failed due to an internal service error.  "
                "The service is still operational.")
            redfish_error.add_extended_info("InternalError")
            error_str = redfish_error.serialize()
            return Response(
                response=error_str,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                mimetype="application/json")

        # creates a test client
        self.app = self.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    @mock.patch('oneview_redfish_toolkit.util.all_subscriptions')
    def test_get_subscription_collection(self, subscriptions_mockup):
        """Tests SubscriptionCollection blueprint result against know value"""

        subscriptions_mockup.return_value = dict()

        response = \
            self.app.get("/redfish/v1/EventService/EventSubscriptions/")

        result = json.loads(response.data.decode("utf-8"))

        with open(
            'oneview_redfish_toolkit/mockups/'
            'redfish/SubscriptionCollection.json'
        ) as f:
            subscription_collection_mockup = json.loads(f.read())

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertEqual(subscription_collection_mockup, result)
