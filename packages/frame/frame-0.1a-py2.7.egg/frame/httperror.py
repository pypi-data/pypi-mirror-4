from response import Response


class HTTPError(Exception):
	'''
	The main HTTP error class; anything that derives from this exception class is handled
	specially by Frame. These exceptions are really built halfway like a response and in
	fact include a fake response object so that they can be passed off to be rendered
	as if they are in fact, a response.
	
	`Note`: :exc:`HTTPError` exceptions and derivates default with headers to prevent
	caching. Specifically, the following is set::
	
		headers = {
			'Content-Type': 'text/html',
			'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
			'Pragma': 'no-cache'
		}
	'''
	
	def __init__(self, status, headers={}, *args, **kwargs):
		'''
		Initialize the HTTP Error.
		
		:param status: The status line to send the WSGI server
		:param headers: Headers to apply to the error
		'''
		
		base_headers = DotDict(_default_error_headers)
		base_headers.update(headers)
		
		#: Stores any extra positional arguments; not actually used as of now
		self.args = args
		
		#: Stores any keyword arguments; these are passed to the template when rendered
		self.kwargs = kwargs
		
		#: A fake response object that stores the status line and headers
		self.response = Response.from_data(status, base_headers, None)
		
	def render(self, app):
		'''
		Renders the error template, which is assumed to be in the template directory at
		``errors/{error_code}.html``.
		
		:param app: The Frame application
		:return: The rendered error
		'''
		
		app.response = self.response
		status_code = self.response.status.split(None, 1)[0]
		template_path = 'errors/%s.html' % status_code
		
		self.response.body = app.environment.get_template(template_path).render(
			app=app, status=self.response.status, **self.kwargs)