urls = [
    ('home', '/'),
    ('admin', '/admin'),

    # auth
    ('register', '/api/register'),
    ('login', '/api/login'),
    ('login_oauth2', '/login/{provider}'),
    ('oauth2_callback', '/login/{provider}/callback'),
    ('logout', '/api/logout'),
    ('change_password', '/api/change_password'),
    ('password_recall', '/api/recall_password'),
    ('password_recall_callback', '/api/recall_password_callback'),
    ('logged_user', '/api/user/logged'),

    # api
    ('offer', '/api/offers/{offer_id:\d+}'),
    ('offer_new', '/api/offers/new'),
    ('offer_delete', '/api/offer/{offer_id}/delete'),
    ('offer_activate', '/api/offer/{offer_id}/activate'),
    ('offer_deactivate', '/api/offer/{offer_id}/deactivate'),
    ('related_offers', '/api/offer/{offer_id}/related'),
    ('offer_promotion', '/api/offer/{offer_id}/promotion/{promotion}'),
    ('offers', '/api/offers'),
    ('offers_search', '/api/offers/search'),
    ('offers_promoted', '/api/offers/promoted'),
    ('logo', '/api/logo'),
    ('gallery', '/api/gallery'),
    ('avatar', '/api/avatar'),
    ('tags', '/api/tags'),
    ('tag_autocomplete', '/api/tags/autocomplete'),
    ('tag_names', '/api/tags/names'),
    ('categories', '/api/categories'),
    ('subcategories', '/api/subcategories'),
    ('feedbacks', '/api/feedbacks'),
    ('feedback_check', '/api/feedback/{id}/check'),
    ('account_liking_level', '/api/accounts/liking/{liking_id}/level'),
    ('offer_recommendations', '/api/offers/recommendations'),

    # A/B experiments
    ('experiments', '/api/experiments'),
    ('activate_experiment', '/api/experiment/{name}/activate'),
    ('deactivate_experiment', '/api/experiment/{name}/deactivate'),
    ('experiment_variation', '/api/experiment/{name}/variation'),
    ('experiment_increment', '/api/experiment/{name}/{variation}/increment'),

    # database management
    ('migration_export', '/api/database/migration/export'),
    ('migration_import', '/api/database/migration/import'),
    ('update_schema', '/api/database/update'),
    # dev only - disable on production
    ('clear_database', '/api/database/clear'),
    ('generate_random_instance', '/api/database/generate'),
    ('list_incomplete', '/api/database/incomplete'),

    # misc
    ('task_progress', '/api/task/{id}/progress'),
    ('task_cancel', '/api/task/{id}/cancel'),

    # seo
    ('seo_home', '/seo'),
    ('seo_search', '/offers/search'),
    ('seo_offer', '/offers/{id}'),

]
