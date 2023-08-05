from django.conf import settings
from django.http import HttpResponseRedirect, get_host

SSL = 'SSL'

class SSLRedirect:
	def process_view(self, request, view_func, view_args, view_kwargs):
		secure = None
		we_are_secure = any([settings.DEBUG, request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https'])
		if SSL in view_kwargs and settings.DEBUG is False:
			secure = view_kwargs[SSL]
			del view_kwargs[SSL]
		if secure is not None and settings.DEBUG is False:
			if secure and not we_are_secure:
				return self._redirect(request, secure)
			
	def _redirect(self, request, secure):
		protocol = secure and "https" or "http"
		newurl = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())
		return HttpResponseRedirect(newurl)


class WWWRedirect:
	def process_view(self, request, view_func, view_args, view_kwargs):
		we_are_www = any([settings.DEBUG, request.META['HTTP_HOST'].startswith('www.')])
		if not we_are_www:
			secure = any([request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https'])
			return self._redirect(request, secure)

	def _redirect(self, request, secure):
		protocol = secure and "https" or "http"
		newurl = "%s://%s.%s%s" % (protocol, 'www', get_host(request), request.get_full_path())
		return HttpResponseRedirect(newurl)