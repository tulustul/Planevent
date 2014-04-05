urls = [
    ('home', '/'),
    ('admin', '/admin'),

    # auth
    ('register', '/api/register'),
    ('login', '/api/login'),
    ('login_oauth2', '/login/{provider}'),
    ('oauth2_callback', '/login/{provider}/callback'),
    ('logout', '/api/logout'),
    ('password_recall', 'api/recall_password'),
    ('password_recall_callback', '/password_recall_callback'),
    ('logged_user', '/api/user/logged'),

    # api
    ('offer', '/api/offer/{id}'),
    ('related_offers', '/api/offer/{id}/related'),
    ('offer_promotion', '/api/offer/{id}/promotion/{promotion}'),
    ('offers', '/api/offers'),
    ('offers_search', '/api/offers/search'),
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
