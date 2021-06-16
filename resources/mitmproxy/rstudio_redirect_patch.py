"""If running the client as a service, make sure RStudio redirects function properly"""
from mitmproxy import http
import os


def response(flow: http.HTTPFlow) -> None:
    if flow.response.status_code == 302:
        # EXTERNAL_URL is the `proxy.external_url` value from the config file
        # This is `http://localhost:10000` by default, and can be set when running
        # the client as a service
        external_url = os.environ.get("EXTERNAL_URL")
        # PROXY_PATH is the path in the CHP proxy to the parent RStudio
        # container (i.e. /rstudio/<parent container id>)
        proxy_path = os.environ.get("PROXY_PATH")

        location = flow.response.headers.get("location")
        if location:
            if location.endswith("auth-sign-in"):
                # You are loading RStudio for the first time, and it's redirecting you to "log in".
                # This will then redirect you again with a cookie
                flow.response.headers["location"] = f"{external_url}{proxy_path}auth-sign-in"
            elif location == "https://localhost:8080/":
                # You are logged in and getting the cookie. Redirect back to the root of the app
                flow.response.headers["location"] = f"{external_url}{proxy_path}"

