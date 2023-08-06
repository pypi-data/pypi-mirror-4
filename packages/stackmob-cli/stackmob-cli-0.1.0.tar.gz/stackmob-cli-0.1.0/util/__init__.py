import os
import json

api_key_name = "api_key"
api_secret_name = "api_secret"

def hasattrs(obj, attrs):
	has = True
	for attr in attrs:
		has and hasattr(obj, attr)
	return has

def _read_api_key_and_secret(args_dict):
	cli_filename = os.path.expanduser("~/.stackmob-cli")
	if api_key_name in args_dict and api_secret_name in args_dict and type(args_dict[api_key_name])==str and type(args_dict[api_secret_name])==str:
		return args_dict[api_key_name], args_dict[api_secret_name]
	elif os.path.exists(cli_filename):
		handle = open(cli_filename)
		json_string = str(handle.read())
		try:
			cli_json = json.loads(json_string)
			if api_key_name in cli_json and api_secret_name in cli_json:
				return cli_json[api_key_name], cli_json[api_secret_name]
			else:
				return None, None
		finally:
			handle.close()
	else:
		return None, None
		
def read_api_key_and_secret_or_die(args_dict):
	api_key, api_secret = _read_api_key_and_secret(args_dict)
	if api_key == None or api_secret == None:
		print textwrap.dedent("""
		api_key and api_secret must both be specified on the command line, or both must be specified in a ~/.stackmob-cli file like this:

		{
			"%s": "YOUR_API_KEY",
			"%s": "YOUR_API_SECRET"
		}

		"""%(api_key_name, api_secret_name))
		sys.exit(1)
	return api_key, api_secret
