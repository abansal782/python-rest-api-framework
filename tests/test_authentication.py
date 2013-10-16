from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp
import json
from rest_api_framework.authentication import (ApiKeyAuthorization,
                                               ApiKeyAuthentication)
from rest_api_framework.datastore import PythonListDataStore
from rest_api_framework import models
from rest_api_framework.controllers import WSGIDispatcher


class ApiModel(models.Model):
    fields = [
        models.StringPkField(name="id", required=True)
        ]


class TestAuthentication(TestCase):

    def test_unauth_get_list(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(resp.status_code, 401)

    def test_auth_get_list(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)
        resp = client.get("/address/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/address/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

    def test_auth_unique_uri(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)

        resp = client.get("/address/1/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/address/1/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

    def test_post_auth(self):
        """
        Test a read only api.
        GET should be ok, POST and PUT should not
        """

        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET"],
                "unique_verbs": ["GET"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }
        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)

        resp = client.get("/address/1/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.post("/address/?apikey=azerty",
                           data=json.dumps({'name': 'bob', 'age': 34}))
        self.assertEqual(resp.status_code, 405)

    def test_badlyconfigured_api(self):

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET"],
                "unique_verbs": ["GET"],
                "options": {"authorization": ApiKeyAuthorization}
                }
        self.assertRaises(ValueError, ApiAppAuth, "")
