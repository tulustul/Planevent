urls = [
    ('home', '/'),
    ('admin', '/admin'),

    # login handlers
    ('login_oauth2', '/login/{provider}'),
    ('oauth2_callback', '/login/{provider}/callback'),

    # api
    ('vendor', '/api/vendor/{id}'),
    ('related_vendors', '/api/vendor/{id}/related'),
    ('vendor_promotion', '/api/vendor/{id}/promotion/{promotion}'),
    ('vendors', '/api/vendors'),
    ('vendors_search', '/api/vendors/search'),
    ('image', '/api/image'),
    ('gallery', '/api/gallery'),
    ('tags', '/api/tags'),
    ('tag_autocomplete', '/api/tags/autocomplete/{tag}'),
]
