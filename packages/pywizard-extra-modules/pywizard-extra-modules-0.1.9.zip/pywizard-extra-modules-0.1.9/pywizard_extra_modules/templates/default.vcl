# This is a basic VCL configuration file for varnish.  See the vcl(7)
# man page for details on VCL syntax and semantics.
# 
# Default backend definition.  Set this to point to your content
# server.
# 
backend default {
    .host = "127.0.0.1";
    .port = "9080";
}

# Set a local ACL.
#acl localhost {
#  "localhost";
#}

sub vcl_recv {
  #if (!req.http.X-Forward-For && client.ip !~ localhost) {
  #  set req.http.x-Redir-Url = "https://" + req.http.host + req.url;
  #  error 750 req.http.x-Redir-Url;
  #}
   
  set req.backend = default;
  set req.grace = 30s;
   
  # Pass the correct originating IP address for the backends
  if (req.restarts == 0) {
    if (req.http.X-Forwarded-For) {
      set req.http.X-Forwarded-For = req.http.X-Forwarded-For + ", " + client.ip;
    } else {
      set req.http.X-Forwarded-For = client.ip;
    }
  }
   
  # Remove any port that might be stuck in the hostname.
  set req.http.Host = regsub(req.http.Host, ":[0-9]+", "");

}


include "sites.vcl";

sub vcl_recv {
  set req.backend = default;
  return(pass);
}


sub vcl_error {
  # For redirecting traffic from HTTP to HTTPS - see where error 750 is set in
  # vcl_recv().
  if (obj.status == 750) {
    set obj.http.Location = obj.response;
    set obj.status = 302;
    return (deliver);
  }
}

sub vcl_pipe {
  # To keep websocket traffic happy we need to copy the upgrade header.
  if (req.http.upgrade) {
    set bereq.http.upgrade = req.http.upgrade;
  }

  set bereq.http.Connection = "close";

  return (pipe);
}
