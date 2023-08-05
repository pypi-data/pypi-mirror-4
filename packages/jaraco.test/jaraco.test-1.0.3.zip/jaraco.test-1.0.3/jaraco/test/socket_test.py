try:
    from cherrypy.process.servers import (wait_for_free_port,
        wait_for_occupied_port, check_port)
except ImportError:
    # borrowed from cherrypy==3.2.0rc1 (r2684)
    import socket
    import time
    def client_host(server_host):
        """Return the host on which a client can connect to the given listener."""
        if server_host == '0.0.0.0':
            # 0.0.0.0 is INADDR_ANY, which should answer on localhost.
            return '127.0.0.1'
        if server_host in ('::', '::0', '::0.0.0.0'):
            # :: is IN6ADDR_ANY, which should answer on localhost.
            # ::0 and ::0.0.0.0 are non-canonical but common ways to write IN6ADDR_ANY.
            return '::1'
        return server_host

    def check_port(host, port, timeout=1.0):
        """Raise an error if the given port is not free on the given host."""
        if not host:
            raise ValueError("Host values of '' or None are not allowed.")
        host = client_host(host)
        port = int(port)

        import socket

        # AF_INET or AF_INET6 socket
        # Get the correct address family for our host (allows IPv6 addresses)
        try:
            info = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM)
        except socket.gaierror:
            if ':' in host:
                info = [(socket.AF_INET6, socket.SOCK_STREAM, 0, "", (host, port, 0, 0))]
            else:
                info = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (host, port))]

        for res in info:
            af, socktype, proto, canonname, sa = res
            s = None
            try:
                s = socket.socket(af, socktype, proto)
                # See http://groups.google.com/group/cherrypy-users/
                #        browse_frm/thread/bbfe5eb39c904fe0
                s.settimeout(timeout)
                s.connect((host, port))
                s.close()
                raise IOError("Port %s is in use on %s; perhaps the previous "
                              "httpserver did not shut down properly." %
                              (repr(port), repr(host)))
            except socket.error:
                if s:
                    s.close()

    def wait_for_free_port(host, port):
        """Wait for the specified port to become free (drop requests)."""
        if not host:
            raise ValueError("Host values of '' or None are not allowed.")

        for trial in range(50):
            try:
                # we are expecting a free port, so reduce the timeout
                check_port(host, port, timeout=0.1)
            except IOError:
                # Give the old server thread time to free the port.
                time.sleep(0.1)
            else:
                return

        raise IOError("Port %r not free on %r" % (port, host))

    def wait_for_occupied_port(host, port):
        """Wait for the specified port to become active (receive requests)."""
        if not host:
            raise ValueError("Host values of '' or None are not allowed.")

        for trial in range(50):
            try:
                check_port(host, port)
            except IOError:
                return
            else:
                time.sleep(.1)

        raise IOError("Port %r not bound on %r" % (port, host))
