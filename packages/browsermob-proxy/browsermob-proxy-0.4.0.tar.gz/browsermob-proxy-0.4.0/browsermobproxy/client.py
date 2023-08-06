import requests
from urllib import urlencode
import json


class Client(object):
    def __init__(self, url):
        """
        Initialises a new Client object
        :Args:
         - url: This is where the BrowserMob Proxy lives
        """
        self.host = url
        resp = requests.post('%s/proxy' % self.host, urlencode(''))
        jcontent = json.loads(resp.content)
        self.port = jcontent['port']
        url_parts = self.host.split(":")
        self.proxy = url_parts[0] + ":" + url_parts[1] + ":" + str(self.port)

    def headers(self, headers):
        """
        This sets the headers that will set by the proxy on all requests
        :Args:
         - headers: this is a dictionary of the headers to be set
         """
        if not isinstance(headers, dict):
            raise TypeError("headers needs to be dictionary")

        r = requests.post(url='%s/proxy/%s/headers' % (self.host, self.port),
                          data=json.dumps(headers),
                          headers={'content-type': 'application/json'})
        return r.status_code

    def new_har(self, ref=None):
        """
        This sets a new HAR to be recorded
        :Args:
         - ref: A reference for the HAR. Defaults to None
        """
        if ref:
            payload = {"initialPageRef": ref}
        else:
            payload = {}
        r = requests.put('%s/proxy/%s/har' % (self.host, self.port), payload)
        return (r.status_code, r.json)

    def new_page(self, ref=None):
        """
        This sets a new page to be recorded
        :Args:
         - ref: A reference for the new page. Defaults to None
        """
        if ref:
            payload = {"pageRef": ref}
        else:
            payload = {}
        r = requests.put('%s/proxy/%s/har/pageRef' % (self.host, self.port),
                         payload)
        return r.status_code

    @property
    def har(self):
        """
        Gets the HAR that has been recorded
        """
        r = requests.get('%s/proxy/%s/har' % (self.host, self.port))

        return r.json

    def selenium_proxy(self):
        """
        Returns a Selenium WebDriver Proxy class with details of the HTTP Proxy
        """
        from selenium import webdriver
        return webdriver.Proxy({"httpProxy": self.proxy})

    def webdriver_proxy(self):
        """
        Returns a Selenium WebDriver Proxy class with details of the HTTP Proxy
        """
        return self.selenium_proxy()

    def add_to_webdriver_capabilities(self, capabilities):
        """
        Adds an 'proxy' entry to a desired capabilities dictionary with the
        BrowserMob proxy information
        """
        capabilities['proxy'] = {'proxyType': 'manual',
                                 'httpProxy': self.proxy}

    def whitelist(self, regexp, status_code):
        """
        Sets a list of URL patterns to whitelist
        :Args:
         - regex: a comma separated list of regular expressions
         - status_code: the HTTP status code to return for URLs that do not
           match the whitelist
        """
        r = requests.put('%s/proxy/%s/whitelist' % (self.host, self.port),
                         urlencode({'regex': regexp, 'status': status_code}))
        return r.status_code

    def blacklist(self, regexp, status_code):
        """
        Sets a list of URL patterns to blacklist
        :Args:
         - regex: a comma separated list of regular expressions
         - status_code: the HTTP status code to return for URLs that do not
           match the blacklist

        """
        r = requests.put('%s/proxy/%s/blacklist' % (self.host, self.port),
                         urlencode({'regex': regexp, 'status': status_code}))
        return r.status_code

    def basic_authentication(self, domain, username, password):
        """
        This add automatic basic authentication
        :Args:
         - domain: domain to set authentication credentials for
         - username: valid username to use when authenticating
         - password: valid password to use when authenticating
         """
        r = requests.post(url='%s/proxy/%s/auth/basic/%s' % (self.host, self.port, domain),
                          data=json.dumps({'username': username, 'password': password}),
                          headers={'content-type': 'application/json'})
        return r.status_code

    LIMITS = {
        'upstream_kbps': 'upstreamKbps',
        'downstream_kbps': 'downstreamKbps',
        'latency': 'latency'
    }

    def limits(self, options):
        """
        Limit the bandwidth through the proxy.
        :Args:
         - options: A dictionary with all the details you want to set.
                        downstreamKbps - Sets the downstream kbps
                        upstreamKbps - Sets the upstream kbps
                        latency - Add the given latency to each HTTP request
        """
        params = {}

        for (k, v) in options.items():
            if k not in self.LIMITS:
                raise KeyError('invalid key: %s' % k)

            params[self.LIMITS[k]] = int(v)

        if len(params.items()) == 0:
            raise KeyError("You need to specify one of the valid Keys")

        r = requests.put('%s/proxy/%s/limit' % (self.host, self.port),
                         urlencode(params))
        return r.status_code

    def remap_hosts(self, address, ip_address):
        """
        Remap the hosts for a specific URL
        :Args:
         - address - url that you wish to remap
         - ip_address - IP Address that will handle all traffic for the address passed in
        """
        assert address is not None and ip_address is not None
        r = requests.post('%s/proxy/%s/hosts' % (self.host, self.port), 
                         json.dumps({address: ip_address}),
                          headers={'content-type': 'application/json'})
        return r.status_code

    def close(self):
        """
        shuts down the proxy and closes the port
        """
        r = requests.delete('%s/proxy/%s' % (self.host, self.port))
        return r.status_code
