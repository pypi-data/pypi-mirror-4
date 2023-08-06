
backend app {
    .host = "127.0.0.1";
    .port = "9180";
}

backend app_nodejs {
  .host = "127.0.0.1";
  .port = "9090";
  .connect_timeout = 1s;
  .first_byte_timeout = 2s;
  .between_bytes_timeout = 60s;
  .max_connections = 800;
}

sub vcl_recv {
   	# Pipe websocket connections directly to Node.js.
  	if (req.http.Upgrade ~ "(?i)websocket") {
        set req.backend = app_nodejs;
        return (pipe);
    }

    {% for expr in node_urls %}
    if (req.url ~ "{{ expr }}") {
        set req.backend = app_nodejs;
        return (pipe);
    }
    {% endfor %}

	set req.backend = app;

    return(pass);
}
