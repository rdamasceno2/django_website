import sys
import os
from ConfigParser import SafeConfigParser
from subprocess import call

def set_env_vars(config_file):
  parser = SafeConfigParser()
  parser.read(config_file)

  env_base = "CONFIG_PARSER"

  final_env = {}

  for s in parser.sections():
    sec = s.upper()
    for o in parser.options(s):
      final_env["___".join([env_base,sec,o.upper()])] = parser.get(s,o)

#final_string = " ".join(["%(env)s=%(val)s" % {"env":k,"val":final_env[k]} for k in final_env.keys()])

#print final_string

  final_strings = ["%(env)s=%(val)s" % {"env":k,"val":final_env[k]} for k in final_env.keys()]


  for k in final_env.keys():
    print k
    if len(sys.argv) > 2:
      del os.environ[k]
    else:
      os.environ[k] = str(final_env[k])

if __name__ == "__main__":
  set_env_vars(sys.argv[1])

