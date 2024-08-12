import re, socket, threading, json
from http.client import responses

class Server:
    routes = {}
    before_all_middlewares = []


    def start_server(self, host='localhost', port = 9090):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.listen()
            print(f'Server listening on {host}:{port}')
            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=self.__handle_connection, args=(conn,)).start()


    def register_handler(self, path: str, handler):
        if not self.__is_path_valid(path):
            raise ValueError('invalid provided path:', path)
        self.routes[path] = handler


    def register(self, path, middleware = None):
        if not self.__is_path_valid(path):
            raise ValueError('invalid provided path:', path)

        def decorator(func):
            if middleware:
                if isinstance(middleware, list):
                    self.routes[path] = self.__chain_middlewares(middleware, func)
                else:
                    self.routes[path] = middleware(func)
            else:
                self.routes[path] = func

        return decorator


    def before_all(self):
        def decorator(func):
            self.before_all_middlewares.append(func)
        return decorator


    def __handle_connection(self, conn: socket.socket):
        with conn:
            while True:
                data = conn.recv(1024 * 2)
                if not data:
                    break

                try:
                    reqstr = data.rstrip(b'\x00').decode()
                    parsed = self.__parse_request(reqstr)
                except:
                    return conn.sendall(self.__create_response('can not parse request', 400))

                path_key = parsed["verb"] + ' ' + parsed["path"]

                if path_key in self.routes:
                    try:
                        result = self.__create_handler(self.routes[path_key])(parsed)
                        if not isinstance(result, tuple):
                            return conn.sendall(self.__create_response(self.__serialize_response(result)))

                        resultLen = len(result)
                        if resultLen == 3:
                            response, code, headers = result
                            return conn.sendall(self.__create_response(self.__serialize_response(response), code, headers))
                        if resultLen == 2:
                            response, code = result
                            return conn.sendall(self.__create_response(self.__serialize_response(response), code))
                        # 500 - invalid number of return values
                        conn.sendall(self.__create_response('', 500))
                        raise ValueError('internal server error: handler returned bad number of values:', resultLen)
                    except Exception as e:
                        self.__create_internal_error_response(conn)
                        raise RuntimeError('internal server error:', e)
                # 404 - route not found
                self.__create_internal_error_response(conn, '', 404)


    def __create_handler(self, handler):
        if self.before_all_middlewares:
            return self.__chain_middlewares(self.before_all_middlewares, handler)
        else:
            return handler

    def __create_internal_error_response(self, conn: socket.socket, msg = '', code = 500):
        conn.sendall(self.__create_response(msg, code))

    def __serialize_response(self, result):
        if isinstance(result, dict) or isinstance(result, list):
            return json.dumps(result)
        return result

    def __create_response(self, resp, code = 200, headers = {}, contentType = 'application/json'):
        resp = resp if isinstance(resp, str) else str(resp)
        code_message = responses.get(code, 'Eshta')
        http_resp = (
            f'HTTP/1.1 {code} {code_message}\r\n'
            f'Content-Type: {contentType}\r\n'
            f'Content-Length: {len(resp)}\r\n'
        )
        for header, value in headers.items():
            header, value = str(header), str(value)
            http_resp += f'{header}: {value}\r\n'
        return (http_resp + f'\r\n{resp}').encode()

    def __parse_request(self, request_string: str):
        headers = {}
        sep = '\r\n'
        try:
            head, body = request_string.split(sep + sep)
            headlines = head.split(sep)
            request_line, headlines = headlines[0], headlines[1:]
            verb, path, _ = request_line.split(' ')
            for line in headlines:
                idx = line.index(':')
                header, value = line[:idx], line[idx+2:]
                headers[header] = value
            return {
                'verb': verb,
                'path': path,
                'headers': headers,
                'body': body
            }
        except:
            raise ValueError('could not parse request')


    def __is_path_valid(self, path: str) -> bool:
        pattern = r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) /[^\s]*$'
        return bool(re.match(pattern, path))


    def __chain_middlewares(self, middlewares, func):
        for middleware in reversed(middlewares):
            func = middleware(func)
        return func
