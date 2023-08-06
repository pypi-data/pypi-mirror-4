from django.conf import settings


DEFAULT_THEME = {
    'LINK_COLOR': '#5db39a',
    'LINK_HOVER': '',
    'HEADING_COLOR': '',
    'INDEX_HEADING_COLOR': '',
    'HEADER_BACKGROUND': '',
    'CONTENT_BACKGROUND': '',
    'FOOTER_BACKGROUND': '',
    'HOME_TITLE': 'Nice to meet you!!',
    'HOME_SUBTITLE': 'Say hello to federated worldwide services',
    'JQUERY_UI_THEME': 'custom-theme',
}


def peer_theme(request):
    user_theme = getattr(settings, 'PEER_THEME', DEFAULT_THEME)
    theme = {}
    theme.update(DEFAULT_THEME)
    theme.update(user_theme)
    return theme


def auth(request):
    return {
        'SAML_ENABLED': getattr(settings, 'SAML_ENABLED', False),
        'REMOTE_USER_ENABLED': getattr(settings, 'REMOTE_USER_ENABLED', False),
        }
