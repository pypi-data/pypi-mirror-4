import sys
import datetime
from _config import config
from pytz import timezone


class Logger(object):
	def populate_format_data(self, request, status, headers, response_body):
		now = datetime.datetime.now()
		local_tz = timezone(config['timezone'])
		
		dt_aware = local_tz.localize(now)
		
		timestamp = dt_aware.strftime("%d/%b/%Y:%H:%M:%S %z")
		
		try:
			status_code, status_message = status.split(None, 1)
		except ValueError:
			status_code = 'INVALID'
			status_message = 'INVALID'
			
		if 'user_agent' in request.headers:
			user_agent = request.headers.user_agent 
		else:
			user_agent = '-'
			
		if 'referer' in request.headers:
			referer = request.headers.referer
		else:
			referer = '-'
		
		return {
			'remote_host': request.headers.remote_addr,
			'timestamp': timestamp,
			'request_line': "%s %s %s" % (
				request.headers.request_method,
				request.headers.request_uri,
				request.headers.server_protocol),
			'status_code': status_code,
			'body_size': len(response_body),
			'local_address': request.headers.server_addr,
			'environment': request.environ,
			'request_protocol': request.headers.server_protocol,
			'request_method': request.headers.request_method,
			'server_port': request.headers.server_port,
			'query_string': request.headers.query_string,
			'request_uri': request.headers.request_uri,
			'server_name': request.headers.server_name,
			'user_agent': user_agent,
			'referer': referer
		}
		
	def log_request(self, request, status, headers, response_body):
		format_data = self.populate_format_data(request, status, headers, response_body)
		
		self.out.write(
			"%(remote_host)s [%(timestamp)s] \"%(request_line)s\" %(status_code)s "
			"%(body_size)s \"%(referer)s\" \"%(user_agent)s\"\n" % format_data)
	
	def log_error(self, message):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
		self.err.write("%s: %s\n" % (timestamp, message))

		
class StdoutLogger(Logger):
	def __init__(self, out=sys.stdout, err=sys.stderr, *args, **kwargs):
		self.out = out
		self.err = err
		
		
logger = StdoutLogger()