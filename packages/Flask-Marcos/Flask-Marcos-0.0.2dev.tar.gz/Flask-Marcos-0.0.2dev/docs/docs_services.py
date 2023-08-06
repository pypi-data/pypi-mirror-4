def start_docs_service(app):
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        import os
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/docs': os.path.join(os.path.dirname(__file__), 'build/html')
        })
