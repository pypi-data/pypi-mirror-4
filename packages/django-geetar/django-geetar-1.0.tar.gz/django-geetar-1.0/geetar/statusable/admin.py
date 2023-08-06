from django.contrib import admin


class StatusableAdminMixin(object):

    """
    Simple admin for StatusableModel instances adding batch
    activate/deactivate functionality
    """

    actions = ['activate', 'deactivate']

    def _result_string(self, result):
        plural = not result == 1
        return '%d Item%s %s' % (result, 's' if plural else '',
                                   'were' if plural else 'was',)

    def activate(self, request, queryset):
        result = queryset.activate()
        msg = self._result_string(result)
        self.message_user(request, '%s activated' % msg)

    activate.short_description = 'Activate selected %(verbose_name_plural)s'

    def deactivate(self, request, queryset):
        result = queryset.deactivate()
        msg = self._result_string(result)
        self.message_user(request, '%s deactivated' % msg)

    deactivate.short_description = 'Deactivate selected %(verbose_name_plural)s'
