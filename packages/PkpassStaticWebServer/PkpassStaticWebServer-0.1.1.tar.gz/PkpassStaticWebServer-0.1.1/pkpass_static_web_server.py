from SimpleHTTPServer import SimpleHTTPRequestHandler, BaseHTTPServer

class PkPassHTTPRequestHandler(SimpleHTTPRequestHandler):
    SimpleHTTPRequestHandler.extensions_map.update({
        '.pkpass' : 'application/vnd.apple.pkpass',
    })

def main(HandlerClass = PkPassHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    main()


