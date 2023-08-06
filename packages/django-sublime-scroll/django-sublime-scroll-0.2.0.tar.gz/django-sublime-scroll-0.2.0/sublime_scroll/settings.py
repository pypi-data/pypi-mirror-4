from django.conf import settings

SUBLIME_SCROLL_WKHTMLTOIMAGE_PATH = getattr(settings,
    'SUBLIME_SCROLL_WKHTMLTOIMAGE_PATH', 'wkhtmltoimage')

SUBLIME_SCROLL_SETTINGS = getattr(settings, 'SUBLIME_SCROLL_SETTINGS', {
	'scroll_width': 150
})