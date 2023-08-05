# Imports requred for operation
import requests,traceback,sys,json,hashlib,datetime,threading

# Imports for meta-data
import platform,os

class Debugged(object):

	EXC_INFO_FILENAME = 0
	EXC_INFO_LINE_NUMBER = 1
	EXC_INFO_FUNCTION_NAME = 2
	EXC_INFO_TEXT = 3

	base_url = "http://debugged.herokuapp.com/%s"
	api_key = None

	default_data = {}

	@classmethod
	def report(cls,exception, data={}, etype=None, value=None, tback=None):

		if exception:
			etype = type(exception)
			value = exception
			
			try:
				tback = sys.last_traceback
			except:
				tback = sys.exc_info()[2]

		exc_info = traceback.extract_tb(tback)

		now = int(round(float(datetime.datetime.utcnow().strftime("%s.%f")) * 1000)) # convert now to milliseconds
		hash = str(hashlib.sha1(''.join([str( Debugged.api_key ), str(etype), "python", str(now)])).hexdigest())

		finished_local_data = {}

		for key, value in Debugged.default_data.items() + data.items():
			if callable(value):
				value = value()
			finished_local_data.update([item])

		def send():
			# TODO: deal with bad request scenarios
			requests.post( Debugged.base_url  % "report" , auth=(str(Debugged.api_key),""), headers={"Content-Type":"application/json"}, data=json.dumps({
					"created_at": now,
					"identifier": hash,
					"exception_name": str(etype.__name__),
					"sdk_version": "python",
					"stack_trace": ''.join(traceback.format_exception(etype,value,	tback)),
					"line_number": traceback.tb_lineno(tback),
					"character_number": -1,
					"filename": exc_info[Debugged.EXC_INFO_FILENAME],
					"user_custom_data": finished_local_data,
					"sdk_data": {
					}
				})
			)
		threading.Thread(target=send).start() # Send the API request asynchronously 
		return Debugged.base_url % "report/%s" % hash

	@classmethod
	def catch(cls,function,flask=None):
		def fn(type,value=None,tback=None):	
			is_exception = "message" in dir(type)
			if is_exception:
				url = Debugged.report(type)
			else:
				url = Debugged.report(None,type=type, value=value,tback=tback)

			sys.stderr.write(''.join(traceback.format_exception(type,value,tback)))
			function(type,value,tback,url)

			if is_exception: # We probably got here from flask, make sure to return something useful
				_stderr = sys.stderr
				devnull = open(os.devnull, 'w')
				sys.stderr = devnull
				response = Debugged._standard_flask_handle_exception(type)
				sys.stderr = _stderr
				return response

		sys.excepthook = fn

		if flask != None:
			Debugged._standard_flask_handle_exception = flask.handle_exception
			flask.handle_exception = fn
			flask.extensions["debugged"] = cls

class DebuggedMiddleware(Debugged):
	def __init__(self):
		try:
			from django.conf import settings
			Debugged.api_key = settings.DEBUGGED_API_KEY
		except:
			print "Failed to find debugged API key"
	def process_exception(self,request,exception):
		Debugged.report(exception,data={
			"path": request.path,
			"method": request.method,
			"POST data": dict(request.POST),
			"GET data": dict(request.GET),
			"Cookies": dict(request.COOKIES),
			"Meta info": dict(request.META)
		})
		return None

Debugged.catch(lambda a,b,c,d: '')

