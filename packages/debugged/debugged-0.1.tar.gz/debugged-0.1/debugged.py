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
	def report(cls,exception, data={}, type=None, value=None, tback=None):

		if exception:
			type,value,tback = sys.exc_info()
		
		exc_info = traceback.extract_tb(tback,1)[0]
		now = int(round(float(datetime.datetime.utcnow().strftime("%s.%f")) * 1000)) # convert now to milliseconds
		hash = str(hashlib.sha1(''.join([str( Debugged.api_key ), str(type), "python", str(now)])).hexdigest())

		finished_local_data = {}

		for item in Debugged.default_data.items():
			if type(item[1]) == type(lambda x:x):
				item[1] = item[1]()
			finished_local_data.update([item])

		for item in data.items():
			if type(item[1]) == type(lambda x:x):
				item[1] = item[1]()
			finished_local_data.update([item])

		def send():
			# TODO: deal with bad request scenarios
			requests.post( Debugged.base_url  % "report" , auth=(str(Debugged.api_key),""), headers={"Content-Type":"application/json"}, data=json.dumps({
					"created_at": now,
					"identifier": hash,
					"exception_name": str(type.__name__),
					"sdk_version": "python",
					"stack_trace": ''.join(traceback.format_exception(type,value,tback)),
					"line_number": traceback.tb_lineno(tback),
					"character_number": -1,
					"filename": exc_info[Debugged.EXC_INFO_FILENAME],
					"user_custom_data": finished_local_data,
					"sdk_data": {
						"Python Version": str(platform.python_version()),
						"Computer network name": str(platform.node())
					}
				}) 
			)
		threading.Thread(target=send).start() # Send the API request asynchronously 
		return Debugged.base_url % "report/%s" % hash

	@classmethod
	def catch(cls,function):
		def fn(type,value,tback):
			url = Debugged.report(None,type=type, value=value,tback=tback)
			sys.stderr.write(''.join(traceback.format_exception(type,value,tback)))
			function(type,value,tback,url)
		sys.excepthook = fn

