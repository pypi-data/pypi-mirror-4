"""PythonHeaderParserHandler for websockify.

Apache HTTP Server and mod_python must be configured such that this
function is called to handle WebSocket request.
"""


import websockify

from mod_python import apache


def headerparserhandler(request):
    """Handle request.

    Args:
        request: mod_python request.

    This function is named headerparserhandler because it is the default
    name for a PythonHeaderParserHandler.
    """

    request.log_error('in websockify.headerparserhandler: %s' % request.unparsed_uri)
    #request.log_error('1: %s' % request.unparsed_uri)
    request.log_error('2: %s' % dir(request))
    #request.log_error('3: %s' % request.headers_in)

    headers = request.headers_in
    if (headers.get('Upgrade') and
        headers.get('Upgrade').lower() == 'websocket'):

        #if (headers.get('sec-websocket-key1') or
        #    headers.get('websocket-key1')):
        #    # For Hixie-76 read out the key hash
        #    headers.__setitem__('key3', self.rfile.read(8))
        #    challenge += self._request.connection.read(8)

#    try:
#        options = request.get_options()
#        request.subprocess_env['targetHost'] = options['websockify.targetHost']
#        request.subprocess_env['targetPort'] = options['websockify.targetPort']
#    except:
#        request.log_error("websockify - handshake exception: %s" % (exc_info()[1]))
#        raise handshake.AbortedByUserException("websockify: connection denied: %s" % (exc_info()[1]))
#
#    request.ws_protocol = request.ws_requested_protocols[0]
#    request.log_error("websockify: ws_protocol = '%s' (%s)" % (
#        request.ws_protocol, request.ws_requested_protocols), apache.APLOG_NOTICE)
#
#    if request.ws_protocol not in ['base64', 'binary']:
#        request.log_error(
#                "websockify - unsupport protocol: %s" % request.ws_protocol)
#        raise handshake.AbortedByUserException(
#                "websockify: unsupported protocol: %s" % request.ws_protocol)
#

        wsproxy = websockify.WebSocketProxy(target_host="localhost", target_port=5901,
                wrap_cmd=None, wrap_mode=None, unix_target=False, ssl_target=False)
        response = wsproxy.do_websocket_handshake(request.headers_in, request.unparsed_uri)
        request.log_error('4: %s' % response)

        request.connection.write(response)

        request.log_error('5: connection: %s' % type(request.connection))
        request.log_error('5.1: dir(connection): %s' % dir(request.connection))
        wsproxy.client = request.connection
        wsproxy.new_client()
        request.log_error('6: done proxying')

        # Set assbackwards to suppress response header generation by Apache.
        request.assbackwards = 1
        return apache.DONE  # Return DONE such that no other handlers are invoked.

    #response = WebSocket.do_websocket_handshake(request.headers_in, path)
    #request.connection.write(raw_response)
    ## Set assbackwards to suppress response header generation by Apache.
    #request.assbackwards = 1
    #return apache.DONE  # Return DONE such that no other handlers are invoked.

    return apache.DECLINED

# vi:sts=4 sw=4 et
