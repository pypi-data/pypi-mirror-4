def get_heroku_caches():
	try:
		os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS']
		os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
		os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
		return {
			'default': 
			{
				'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
				'LOCATION': os.environ['MEMCACHIER_SERVERS'],
				'TIMEOUT': 500,
				'BINARY': True,
			}
		}
	except:
		return {
			'default': {
			'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
			}
		}