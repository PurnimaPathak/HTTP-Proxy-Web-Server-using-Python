
import socket
import threading
import signal
import sys
import logging
import time
import os
import urllib.request
import argparse
import datetime
from dateutil import parser

parser = argparse.ArgumentParser()
parser.add_argument("timeout", nargs="?", default=500)
parser.add_argument("port", nargs="?", default=12345)
args = parser.parse_args()
if args.timeout is not None:
    Timeout = args.timeout
Port = args.port
print(Timeout)

CACHE_ = "./Cache/"
first_line = ""

cache = {}
date = {}

logging.basicConfig(filename='example.log', level=logging.DEBUG)


def _gen_headers(code):
    """ Generates HTTP response Headers. Omits the first line! """

    # determine response code
    h = ''
    if code == 200:
        h = 'HTTP/1.0 200 OK\n'
    elif code == 404:
        h = 'HTTP/1.0 404 Not Found\n'  # /sadpa.html
    elif code == 400:  # GETTA , fac ebo#ok.com, HTTP/1.2
        h = 'HTTP/1.0 400 Bad Request\n'
    elif code == 500:
        h = 'HTTP/1.0 500 Internal Server Error\n'
    elif code == 501:  # UPDATE
        h = 'HTTP/1.0 501 Not Implemented\n'
    elif code == 505:
        h = 'HTTP/1.0 505 HTTP Version Not Supported\n'
    elif code == 451:
        h = 'HTTP/1.0 451 Site Blocked\n'

    # write further headers
    current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    h += 'Date: ' + current_date + '\n'
    h += 'Server: Simple-Python-HTTP-Server\n'
    # h += 'Connection: Keep-Alive\n\n'  # signal that the connection wil be closed after completing the request
    # TODO: Connection =close? if TA replies, when error code is thrown
    # TODO: if request says connection=close/ None, header should be connection = close
    h += 'Connection: close\n\n'  # signal that the connection wil be closed after completing the request

    return h


def is_blocked_site(site_name):
    with open("blocked.txt") as blocked_list_file:
        for site in blocked_list_file.readlines():
            if site in site_name:
                return True
    return False


def _gen_headers_for_304(code, Keep_Alive):
    """ Generates HTTP response Headers. Omits the first line! """

    # determine response code
    h = 'HTTP/1.1 304 Not Modified\n'

    # write further headers
    current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    h += 'Date: ' + current_date + '\n'
    h += 'Server: Simple-Python-HTTP-Server\n'
    h += 'Connection: ' + Keep_Alive + '\n\n'  # signal that the connection wil be closed after completing the request
    # h += 'ETag: '+ETag+'\n\n'
    return h


config = {
    "HOST_NAME": "0.0.0.0",
    "MAX_REQUEST_LEN": 1024,
    "CONNECTION_TIMEOUT": 5
}
url_unsafe_characters = [" ", "<", ">", "{", "}", "|", "#", "%", "^", "~", "[", "]", "`"]
valid_http_version = "HTTP/1.0"
valid_http_method = ['GET', "POST", "UPDATE", "HEAD", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]


class Server:
    """ The server class """

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)  # Shutdown on Ctrl+C
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Re-use the socket
        self.serverSocket.bind(
            (config['HOST_NAME'], int(Port)))  # bind the socket to a public host, and a port
        self.serverSocket.listen(10)  # become a server socket
        self.__clients = {}

    def listenForClient(self):
        """ Wait for clients to connect """
        while True:
            (clientSocket, client_address) = self.serverSocket.accept()  # Establish the connection
            d = threading.Thread(name=self._getClientName(client_address),
                                 target=self.proxy_thread(clientSocket, client_address),
                                 args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()
        self.shutdown(0, 0)

    def proxy_thread(self, conn, client_addr):
        """
        *******************************************
        *********** PROXY_THREAD FUNC *************
          A thread to handle request_client from browser
        *******************************************
        """

        request_client = conn.recv(config['MAX_REQUEST_LEN'])  # get the request_client from browser
        first_line = request_client.decode().split('\n')[0]
        request_method = None
        url = None
        http_version = None
        try:
            request_client_proxy = request_client.decode()
            print(request_client_proxy)
            if request_client_proxy:
                request_method = request_client_proxy.split(' ')[0]
                url = request_client_proxy.split(' ')[1]
                # IfModifiedSince_start = request_client_proxy.find("If-Modified-Since: ")
                # IfModifiedSince_start = IfModifiedSince_start + 19
                # IfModifiedSince_end = request_client_proxy.find("If-None-Match: ")
                # IfModifiedSince = request_client_proxy[IfModifiedSince_start:IfModifiedSince_end]
                # IfNoneMatch_start = request_client_proxy.find("If-None-Match: ")
                # IfNoneMatch_start = IfNoneMatch_start + 15
                # IfNoneMatch_end = request_client_proxy.find("Pragma")
                # IfNoneMatch = request_client_proxy[IfNoneMatch_start:IfNoneMatch_end]
                try:
                    urllib.request.urlopen(url)
                except Exception as e:
                    error = str(e)
                    response_content = b"<html><body><p>" + error.encode() + b"</p><p>Python Proxy HTTP " \
                                                                             b"server</p></body></html> "
                    response_headers = _gen_headers(404)
                    proxy_server_response = response_headers.encode() + response_content
                    conn.send(proxy_server_response)
                    conn.close()

                http_version = request_client_proxy.split(' ')[2].split("\r")[0]
            else:
                pass
        except Exception as e:
            pass

        if http_version == 'HTTP/1.0':
            if request_method == 'GET':
                for item in url_unsafe_characters:
                    if item in url:
                        logging.info("Warning, Bad request. Serving response code 400\n")
                        response_content = b"<html><body><p>Error 400: Bad Request</p><p>Python Proxy HTTP server</p></body></html>"
                        response_headers = _gen_headers(400)
                        proxy_server_response = response_headers.encode() + response_content
                        conn.send(proxy_server_response)
                        conn.close()
                        return
                if (http_version != valid_http_version) or (request_method not in valid_http_method):
                    logging.info("Warning, Bad request. Serving response code 400\n")
                    response_content = b"<html><body><p>Error 400: Bad Request</p><p>Python Proxy HTTP server</p></body></html>"
                    response_headers = _gen_headers(400)
                    proxy_server_response = response_headers.encode() + response_content
                    conn.send(proxy_server_response)
                    conn.close()
                else:
                    port, web_server = self.parse_request(request_client_proxy)
                    if os.path.exists(CACHE_ + web_server):
                        tmp_url = url
                        if url.endswith("/"):
                            tmp_url = url + "slash_index_file"
                        if url.__contains__("?"):  # http://morse.colorado.edu/python?y=1234
                            tmp_url = url.split("?")[0]
                        if url.__contains__("http://"):
                            tmp_url = tmp_url.split("http://")[1]
                            tmp_url = CACHE_ + tmp_url
                        if os.path.exists(tmp_url):
                            try:
                                fh = open(tmp_url, "rb")
                                data_cached = fh.read()
                                data = data_cached.decode("latin-1")
                                date_of_response_start_position = data.find("Date: ")
                                date_of_response_start_position = date_of_response_start_position + 6
                                date_of_response_end_position = data.find(" GMT")
                                date_of_response = data[date_of_response_start_position:date_of_response_end_position]
                                date_of_response = datetime.datetime.strptime(date_of_response, "%a, %d %b %Y %H:%M:%S")
                                current_time = datetime.datetime.now()
                                # Keep_Alive = data.split("Keep-Alive: ")[1]
                                # max_age = data.split("max_age: ")[1]
                                # Check if the cache has expired in the proxy
                                date_of_response_plus_timeout = date_of_response + datetime.timedelta(
                                    seconds=int(Timeout))
                                if date_of_response_plus_timeout < current_time:
                                    # check the etags of the stored value and the server value
                                    Expiry_start = data.find("Expires: ")
                                    if Expiry_start != -1:
                                        Expiry_start = Expiry_start + 9
                                        Expiry_end = data.find(" GMT")
                                        Expiry = data[
                                                 Expiry_start:Expiry_end]
                                        Expiry = datetime.datetime.strptime(Expiry,
                                                                            "%a, %d %b %Y %H:%M:%S")

                                        if Expiry < current_time:
                                            # check etags
                                            # etag = data.split("etag: ")[1]
                                            # send the whole request to the server, requesting a new resource
                                            self.create_cache(client_addr, conn, request_client, request_client_proxy,
                                                              url)
                                        else:
                                            # Send a 304 code to the client saying the resource is not stale and pass the
                                            #  cache to the client
                                            response_headers = _gen_headers_for_304(304, "Keep_Alive")
                                            proxy_server_response = response_headers.encode() + data_cached
                                            fh.close()
                                            conn.send(proxy_server_response)
                                            conn.close()
                                            return
                                    else:
                                        Last_Modified_start = data.find("Last-Modified: ")
                                        if Last_Modified_start == -1:
                                            self.create_cache(client_addr, conn, request_client, request_client_proxy,
                                                              url)
                                            return
                                        Last_Modified_start = Last_Modified_start + 15
                                        Last_Modified_end = data.find(" GMT")
                                        Last_Modified = data[
                                                        Last_Modified_start:Last_Modified_end]
                                        Last_Modified = datetime.datetime.strptime(Last_Modified,
                                                                                   "%a, %d %b %Y %H:%M:%S")

                                        if Last_Modified < current_time:
                                            # check etags
                                            # etag = data.split("etag: ")[1]
                                            # send the whole request to the server, requesting a new resource
                                            self.create_cache(client_addr, conn, request_client, request_client_proxy,
                                                              url)
                                            return
                                        else:
                                            # Send a 304 code to the client saying the resource is not stale and pass the
                                            #  cache to the client
                                            response_headers = _gen_headers_for_304(304, "Keep_Alive")
                                            proxy_server_response = response_headers.encode() + data_cached
                                            fh.close()
                                            conn.send(proxy_server_response)
                                            conn.close()
                                            return
                                fh.close()
                                conn.send(data_cached)
                                conn.close()
                                return
                            except Exception as e:
                                # TODO: connection failure check/ socket connection failure error code
                                response_content = b"<html><body><p>Error 500: Internal Server Error</p><p>Python " \
                                                   b"Proxy HTTP server</p></body></html> "
                                response_headers = _gen_headers(500)
                                proxy_server_response = response_headers.encode() + response_content
                                conn.send(proxy_server_response)
                                conn.close()
                                return
                        else:
                            self.create_cache(client_addr, conn, request_client, request_client_proxy, url)
                    else:
                        self.create_cache(client_addr, conn, request_client, request_client_proxy, url)
            else:
                # TODO: Error Handling: HTTP Method not implemented-501 error
                logging.info("Warning, Method not implemented . Serving response code 501\n")
                response_content = b"<html><body><p>Error 501: Not Implemented</p><p>Python Proxy HTTP server</p></body></html>"
                response_headers = _gen_headers(501)
                proxy_server_response = response_headers.encode() + response_content
                conn.send(proxy_server_response)
                conn.close()
                return
        else:
            logging.info("505 HTTP Version Not Supported\n")
            response_content = b"<html><body><p>Error 505: HTTP Version not supported</p><p>Python Proxy HTTP server</p></body></html>"
            response_headers = _gen_headers(505)
            proxy_server_response = response_headers.encode() + response_content
            conn.send(proxy_server_response)
            conn.close()
            return
            # TODO: Error Handling: HTTP Version

    def create_cache(self, client_addr, conn, request_client, request_client_proxy, url):
        cache[url] = b''
        port, web_server = self.parse_request(request_client_proxy)
        if is_blocked_site(web_server):
            response_headers = _gen_headers(451)
            #header = 'HTTP/1.0 451 Site Blocked\n'
            conn.send(response_headers.encode())
            return
        try:
            # create a socket to connect to the web server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(config['CONNECTION_TIMEOUT'])
            s.connect((web_server, port))
            s.send(request_client)  # send request_client to web_server

            while 1:
                data = s.recv(config['MAX_REQUEST_LEN'])  # receive data from web server
                if "pokemon" in data:
                    # Need to check whether data is encoded or not
                    response_headers = _gen_headers(451)
                    # header = 'HTTP/1.0 451 Site Blocked\n'
                    conn.send(response_headers.encode())
                    break
                cache[url] += data
                logging.info("cache updated")
                if len(data) > 0:
                    conn.sendall(data)  # send to browser
                else:
                    decoded_data = cache[url].decode("latin-1")
                    response_code = decoded_data.split()[1]
                    date_of_response_start_position = decoded_data.find("Date: ")
                    date_of_response_start_position = date_of_response_start_position + 6
                    date_of_response_end_position = decoded_data.find(" GMT")
                    date_of_response = decoded_data[date_of_response_start_position:date_of_response_end_position]
                    date[url] = "Date_of_Response: " + date_of_response
                    date_encoded = date[url].encode()
                    cache[url] += date_encoded

                    if response_code == "200":
                        if url.__contains__("?"):
                            url = url.split("?")[0]
                        position_of_file = url.rfind("/")  # http://morse.colorado.edu/
                        url_file = url[position_of_file:]
                        if url_file == "/":
                            url_file = "slash_index_file"
                        url_directory = url[:position_of_file]  # http://morse.colorado.edu
                        if url_directory.__contains__("http://"):
                            url_directory = url_directory.strip("http://")  # morse.colorado.edu
                        file_d = CACHE_ + url_directory  # ./Cache/morse.colorado.edu
                        if not os.path.exists(file_d):
                            os.makedirs(file_d)
                        file_d = file_d + "/" + url_file
                        fh = open(file_d, "wb")
                        fh.write(cache[url])
                        fh.close()
                        break
                    elif response_code == "304":
                        # Exceptional Case
                        # last_modified = 0
                        # request to server again
                        # 200 check
                        # file write
                        pass
                    elif response_code == "404":
                        # No caching
                        # send response to client as we get from server
                        pass
            s.close()
            conn.close()
        except socket.error as error_msg:
            self.log("ERROR", client_addr, error_msg)
            if s:
                s.close()
            if conn:
                conn.close()
            self.log("WARNING", client_addr, "Peer Reset: " + first_line)

    def parse_request(self, request_client_proxy):
        web_server = None
        port = None
        # TODO: Check the host "Host:" on telnet
        list_req = request_client_proxy.split("\r\n")
        for item in list_req:
            if item.__contains__("Host:"):
                list_host = item.split(":")
                if len(list_host) == 2:
                    web_server = list_host[1].strip()
                    port = 80
                elif len(list_host) == 3:
                    web_server = list_host[1].strip()
                    port = list_host[2].strip()
                    port = int(port)
        return port, web_server

    def log(self, log_level, client, msg):
        """ Log the messages to appropriate place """
        LoggerDict = {
            'ThreadName': threading.currentThread().getName()
        }
        if client == -1:  # Main Thread
            formatedMSG = msg
        else:  # Child threads or Request Threads
            formatedMSG = '{0}:{1} {2}'.format(client[0], client[1], msg)
        logging.debug('%s', log_level, formatedMSG, extra=LoggerDict)

    def _getClientName(self, cli_addr):
        """ Return the clientName.
        """
        return "Client"

    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        self.log("WARNING", -1, 'Shutting down gracefully...')
        main_thread = threading.currentThread()  # Wait for all clients to exit
        for t in threading.enumerate():
            if t is main_thread:
                continue
            self.log("FAIL", -1, 'joining ' + t.getName())
            t.join()
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()

