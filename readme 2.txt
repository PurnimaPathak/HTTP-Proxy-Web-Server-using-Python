The proxy_server.py files runs as a proxy to the webserver.
The client sends the request which crosses from the proxy, proxy handles all the errors,
caches the responses from the webserver to serve it the next time it is asked for, form the client.

The proxy_server.py files runs as a proxy to the webserver.
The client sends the request which is intercepted by the proxy, proxy handles all the errors,
caches the responses from the webserver to serve it the next time it is asked for, form the client.
Blocked.txt contains the list of sites which gets blocked. And get a response that the requested site is blocked with error code 451.
Blocking site based on content. If the site contains any word matching that does not conform to the policies and sends an error code 451.
When the client requests the proxy for a webpage for first time the data is fetched from the server and stored in the cache and time is set for that content, and when the same request is sent from the client then the proxy sends gets a 304 response from the server and checks for the expiry time of the cache and sends the cached data if the cache is not expired.