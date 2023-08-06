# coding: utf8

from django import test
from django.core.urlresolvers import reverse


class BaseTestCase(test.TestCase):
    """
    The base test case, providing convenience methods for various testing
    related tasks.
    """
    clients = {}

    def check_template(self, url_name, templated_path, client='default',
                       method='get', **kwargs):
        """
        Checks the given template was used for the given url.
        """
        response = getattr(self, method)(
            url_name=url_name, url_kwargs=kwargs, client=client
        )
        self.assertTemplateUsed(response, templated_path)

    def do_request(self, method, url_name=None, url=None, url_kwargs={},
                   data={}, client='default', **kwargs):
        """
        Performs the request with the given method and returns the response.
        """

        if not url:
            url = self.get_url(url_name, **url_kwargs)

        return getattr(self.get_client(client), method)(
            url, data=data, **kwargs
        )

    def get_client(self, client_name):
        """
        Returns the test client with the given name. If a test client by the
        given name doesn't exist yet one will be created.
        """
        if not client_name in self.clients:
            self.clients[client_name] = test.client.Client()
        return self.clients[client_name]

    def get_url(self, name, **kwargs):
        """ Returns the url for the given name, args and kwargs. """
        return reverse(name, kwargs=kwargs)

    def login(self, client='default', **kwargs):
        """
        Logs the given user in on the given client, defaulting to the `default`
        client.
        """
        return self.get_client(client).login(**kwargs)

    def delete(self, url_name=None, url=None, url_kwargs={}, data={},
               client='default', **kwargs):
        """
        Returns the response for a DELETE request on the url with the given
        name, args and kwargs.
        """

        return self.do_request(
            'delete', url_name, url, url_kwargs, data, client, **kwargs
        )

    def get(self, url_name=None, url=None, url_kwargs={}, data={},
            client='default', **kwargs):
        """
        Returns the response for a POST request on the url with the given name,
        args and kwargs.
        """

        return self.do_request(
            'get', url_name, url, url_kwargs, data, client, **kwargs
        )

    def post(self, url_name=None, url=None, url_kwargs={}, data={},
             client='default', **kwargs):
        """
        Returns the response for a POST request on the url with the given name,
        args and kwargs.
        """

        return self.do_request(
            'post', url_name, url, url_kwargs, data, client, **kwargs
        )

    def put(self, url_name=None, url=None, url_kwargs={}, data={},
            client='default', **kwargs):
        """
        Returns the response for a PUT request on the url with the given name,
        args and kwargs.
        """

        return self.do_request(
            'put', url_name, url, url_kwargs, data, client, **kwargs
        )
