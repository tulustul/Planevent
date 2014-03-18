urls = [
    ('home', '/'),
    ('admin', '/admin'),

    # login handlers
    ('login_oauth2', '/login/{provider}'),
    ('oauth2_callback', '/login/{provider}/callback'),
    ('logout', '/logout'),

    # api
    ('vendor', '/api/vendor/{id}'),
    ('logged_user', '/api/user/logged'),
    ('related_vendors', '/api/vendor/{id}/related'),
    ('vendor_promotion', '/api/vendor/{id}/promotion/{promotion}'),
    ('vendors', '/api/vendors'),
    ('vendors_search', '/api/vendors/search'),
    ('image', '/api/image'),
    ('gallery', '/api/gallery'),
    ('tags', '/api/tags'),
    ('tag_autocomplete', '/api/tags/autocomplete'),
    ('tag_names', '/api/tags/names'),
    ('categories', '/api/categories'),
    ('subcategories', '/api/subcategories'),

    # A/B experiments
    ('experiments', '/api/experiments'),
    ('activate_experiment', '/api/experiment/{name}/activate'),
    ('deactivate_experiment', '/api/experiment/{name}/deactivate'),
    ('experiment_variation', '/api/experiment/{name}/variation'),
    ('experiment_increment', '/api/experiment/{name}/{variation}/increment'),

    # database management
    ('migration', '/api/database/migration'),
    ('update_schema', '/api/database/update'),
    # dev only - disable on production
    ('clear_database', '/api/database/clear'),
    ('generate_random_instance', '/api/database/generate'),
    ('list_incomplete', '/api/database/incomplete'),

    # misc
    ('task_progress', '/api/task/{id}/progress'),
    ('task_cancel', '/api/task/{id}/cancel'),
]
