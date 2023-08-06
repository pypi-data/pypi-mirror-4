import ConfigParser
import os

liveconnect_config_path = '/etc/liveconnect.cfg'
user_config_path = os.path.join(os.path.expanduser('~'), '.liveconnect')
liveconnect_config_locations = [liveconnect_config_path, user_config_path]
if 'LIVECONNECT' in os.environ:
	liveconnect_config_locations = [os.path.expanduser(os.environ['LIVECONNECT'])]
elif 'LIVECONNECT_PATH' in os.environ:
	liveconnect_config_locations = []
	for path in os.environ['LIVECONNECT_PATH'].split(":"):
		liveconnect_config_locations.append(os.path.expanduser(path))