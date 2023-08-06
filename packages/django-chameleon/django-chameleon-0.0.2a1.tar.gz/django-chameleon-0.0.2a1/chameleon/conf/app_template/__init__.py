from django.conf import settings
gettext = lambda s: s

settings.CMS_TEMPLATES += (
    ('{{ app_name }}/{{ app_name }}.html', gettext('Base Template ({{ app_name }})')),
    )

# Enable LESS compile through Django-Compressor
if not 'compressor' in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('compressor',)
if not getattr(settings, 'COMPRESS_OUTPUT_DIR', False):
    settings.COMPRESS_OUTPUT_DIR = 'cache'
if not getattr(settings, 'COMPRESS_CSS_FILTERS', False):
    settings.COMPRESS_CSS_FILTERS = []
if not 'compressor.filters.cssmin.CSSMinFilter' in settings.COMPRESS_CSS_FILTERS:
    settings.COMPRESS_CSS_FILTERS += ('compressor.filters.cssmin.CSSMinFilter',)
if not 'compressor.filters.css_default.CssAbsoluteFilter' in settings.COMPRESS_CSS_FILTERS:
    settings.COMPRESS_CSS_FILTERS += ('compressor.filters.css_default.CssAbsoluteFilter',)
if not 'compressor.filters.template.TemplateFilter' in settings.COMPRESS_CSS_FILTERS:
    settings.COMPRESS_CSS_FILTERS += ('compressor.filters.template.TemplateFilter',)
if not getattr(settings, 'COMPRESS_PRECOMPILERS', False):
    settings.COMPRESS_PRECOMPILERS = []
settings.COMPRESS_PRECOMPILERS += (
    ('text/less', 'lessc {infile} {outfile}'),
    )
if not getattr(settings, 'STATICFILES_FINDERS', False):
    settings.STATICFILES_FINDERS = []
settings.STATICFILES_FINDERS += (
    'compressor.finders.CompressorFinder',
    )
