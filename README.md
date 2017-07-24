# Remme Django module

This module is intended to run on top if Django + nginx bundle.

## nginx configuration
```
server {
        listen 80 default_server;
        listen [::]:80 default_server;
        
        # Enable ssl connections
        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;

        # ...

        # Enable SSL
        ssl on;
        ssl_certificate /path/to/your/ssl/certificate;
        ssl_certificate_key /path/to/your/ssl/key;
        # THIS IS IMPORTANT! This line enables us to use self-signed certificates
        ssl_verify_client optional_no_ca;

        # ...

        # Your Django configuration
        location / {
            # ...
            proxy_pass         http://127.0.0.1:8000;
            proxy_redirect     off;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
            # PASS THE SSL RELATED DATA TO DJANGO
            proxy_set_header   X-SSL-Authenticated $ssl_client_verify;
            proxy_set_header   X-SSL-User-DN $ssl_client_s_dn;
            proxy_set_header   X-SSL-Certificate $ssl_client_raw_cert;
            # ...
        }

        # ...
}
```

## Running Django via WSGI

From `./testapp` directory:

`gunicorn --bind 0.0.0.0:8000 testapp.wsgi`
