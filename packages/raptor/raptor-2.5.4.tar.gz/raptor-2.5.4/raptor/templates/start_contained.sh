#!/bin/bash

# If you're viewing this inside a proc directory on an app host, this is the
# file used to actually start up a Velociraptor-managed process.

# If you're viewing this inside our source code repo, this file is a template
# that will be used to write a real start script at deploy time.  The magic
# strings will be substituted with real values at that time.

export APP_SETTINGS_YAML="/app/settings.yaml"
export PORT=%(port)s
export TMPDIR=/tmp
export HOME=/tmp

CMD="%(cmd)s"
PROCNAME=%(proc_name)s
PROCS_ROOT=%(procs_root)s
exec lxc-start --name $PROCNAME -f $PROCS_ROOT/$PROCNAME/proc.lxc -- su --preserve-environment --shell /bin/bash -c "cd /app;source %(envsh_path)s; exec $CMD" %(user)s
