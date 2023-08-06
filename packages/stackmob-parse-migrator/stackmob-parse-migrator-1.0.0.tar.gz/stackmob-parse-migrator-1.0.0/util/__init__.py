import os
import json
import textwrap
import sys

api_key_name = "api_key"
api_secret_name = "api_secret"
path_name = "path"

def hasattrs(obj, attrs):
	has = True
	for attr in attrs:
		has and hasattr(obj, attr)
	return has

def _read_api_key_and_secret_and_path(args_dict):
	if api_key_name in args_dict and api_secret_name in args_dict and path_name in args_dict and type(args_dict[api_key_name])==str and type(args_dict[api_secret_name])==str and type(args_dict[path_name])==str:
		return args_dict[api_key_name], args_dict[api_secret_name], args_dict[path_name]
	else:
		return None, None, None
		
def read_api_key_and_secret_or_die(args_dict):
	api_key, api_secret, path = _read_api_key_and_secret_and_path(args_dict)
	if api_key == None or api_secret == None or path_name == None:
		print textwrap.dedent("api_key, api_secret and path must both be specified on the command line")
		sys.exit(1)
	return api_key, api_secret, path
