from ConfigParser import SafeConfigParser
import os.path
import sys
import time

default_config = SafeConfigParser()
user_config = SafeConfigParser()
default_config.read('config.cfg.default')
#TODO Add code to verify file exists, and only read if the file exists
if not os.path.isfile('config.cfg'):
  default_config.write(open('config.cfg','w+'))
  print "No existing config file, new file created"
  print "Please make sure to update the existing file"
  sys.exit(0)
user_config.read('config.cfg')
timestamp = '.' + str(int(time.time()*1000))
backup_file = 'config.cfg.user' + timestamp
log_file = 'log' + timestamp
log = open(log_file,'w+')
user_config.write(open(backup_file,'w+'))
new_sections = [x for x in default_config.sections() if x not in user_config.sections()]
deprecated_sections = [x for x in user_config.sections() if x not in default_config.sections()]
existing_sections = [x for x in user_config.sections() if x in default_config.sections()]

log.write("The following sections have been deprecated\n")
for deprecate in deprecated_sections:
  log.write("\t" + deprecate + "\n")
  user_config.remove_section(deprecate)

log.write("The following sections have been added:\n")
for new in new_sections:
  log.write("\t" + new + "\n")
  for opt in default_config.options(new):
    user_config.set(new,opt,default_config.get(new,opt))

log.write("The following sections have been modified:\n")
for existing in existing_sections:
  log.write("\t" + existing + "\n")
  deprecated_options = [x for x in user_config.options(existing) if x not in default_config.options(existing)]
  new_options = [x for x in default_config.options(existing) if x not in user_config.options(existing)]
  for deprecate in deprecated_options:
    log.write("\t\tDEPRECATED: " + deprecate + "\n")
    user_config.remove_option(existing,deprecate)
  for new in new_options:
    log.write("\t\tNEW: " + new + "\n")
    user_config.set(existing,opt,default_config.get(existing,opt))
user_config.write(open('config.cfg','w'))
log.close()
