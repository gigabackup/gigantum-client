from typing import Dict, List, Optional, Tuple
import requests
import base64


class ProxyRouterException(Exception):
    pass


class ProxyRouter(object):
    @classmethod
    def get_proxy(cls, config: Optional[Dict] = None) -> 'ProxyRouter':
        if not config:
            return NullRouter()

        api_port = config.get('api_port')
        api_host = config.get('api_host')
        if not api_port or not api_host:
            return NullRouter()

        return cls(api_host=api_host, api_port=api_port)

    def __init__(self, api_host: str, api_port: int) -> None:
        self.api_host = api_host
        self.api_port = api_port
        self.encode = lambda p: base64.urlsafe_b64encode(p.encode()).decode()

    @property
    def is_null_proxy(self) -> bool:
        return False

    @property
    def routes(self) -> Dict[str, Dict[str, str]]:
        r = requests.get(f'http://{self.api_host}:{self.api_port}/api/routes')
        if r.status_code != 200:
            raise ProxyRouterException(f'Cannot find routes: {r.status_code}')
        else:
            return r.json()

    def add(self, target: str, prefix: Optional[str] = None) -> Tuple[str, str]:
        p = prefix or self.encode(target)
        if p[0] == "/":
            # When setting a route, if a leading slash is included remove it. If you do not do this, you'll get a
            # double leading slash. By handling this here, it greatly simplifies the code, as you can now assume
            # all prefixes will contain a leading slash, since that's how CHP stores them!
            p = p[1:]
        r = requests.post(f'http://{self.api_host}:{self.api_port}/api/routes/{p}',
                          json={'target': target})
        if r.status_code == 201:
            return p, target
        raise ProxyRouterException(f'Cannot set route to {target}: '
                                   f'{r.status_code} {r.text}')

    def remove(self, prefix: str) -> None:
        if prefix[0] == "/":
            # When deleting a route a route, if a leading slash is included remove it. If you do not do this, you'll
            # get a double leading slash. By handling this here, it greatly simplifies the code, as you can now assume
            # all prefixes will contain a leading slash, since that's how CHP stores them!
            prefix = prefix[1:]

        r = requests.delete(f'http://{self.api_host}:{self.api_port}/api/routes/{prefix}')
        if r.status_code == 204:
            return None
        raise ProxyRouterException(f'Cannot delete route {prefix}: '
                                   f'{r.status_code} {r.text}')

    def search(self, target: str) -> Optional[str]:
        """Search for the prefix given a target"""
        routes = self.routes
        for prefix in routes.keys():
            if target == routes[prefix].get('target'):
                return prefix
        return None

    def get_matching_routes(self, endpoint: str, server: str) -> List[str]:
        """Return a list of prefixes matching endpoint (in the target) and server
        (in the route prefix)"""
        routes = self.routes
        return [prefix for prefix in routes.keys()
                if endpoint in routes[prefix]['target']
                and server in prefix]

    def check(self, prefix: str) -> bool:
        """Check if the current prefix still routes to some endpoint
        (Sends HTTP HEAD request, fails if timeout or connection refused) """
        if not prefix:
            return False

        routes = self.routes
        pfx = prefix if prefix[0] == '/' else f'/{prefix}'
        if pfx not in routes.keys():
            return False

        rt = routes[pfx].get('target')
        try:
            requests.head(rt, timeout=1.0)
            return True
        except:
            return False


class NullRouter(ProxyRouter):

    def __init__(self, *args, **kwargs) -> None:
        pass

    @property
    def is_null_proxy(self) -> bool:
        return True

    @property
    def routes(self) -> Dict[str, Dict[str, str]]:
        return {}

    def add(self, target: str, prefix: Optional[str] = None) -> Tuple[str, str]:
        return prefix or "", target

    def remove(self, prefix: str) -> None:
        pass

    def check(self, prefix: str) -> bool:
        return True

    def search(self, target: str) -> bool:
        return False
