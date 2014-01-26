# for openshift only

if __name__ == '__main__':
    import logging.config
    from pyramid.paster import get_app
    from wsgiref.simple_server import make_server

    config = 'production.ini'

    logging.config.fileConfig(config)
    application = get_app(config, 'main')

    # OPENSHIFT_PYTHON_IP:OPENSHIFT_PYTHON_PORT
    httpd = make_server('127.10.51.1', 8080, application)
    httpd.serve_forever()
else:
    from paste.deploy import loadapp
    application = loadapp('config:production.ini', relative_to='.')
