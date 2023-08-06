#!/bin/sh

STATEFILE=/tmp/me2-package-install-state
% for package in packages:
tazpkg -gi ${package} 2>&1 >> /var/log/me2-package.log
rcode=$?
if [ "$rcode" -ne "0" ]; then
 echo "1" > $STATEFILE
 exit 1
fi 
% endfor

echo "Done" >> /var/log/me2-package.log

echo "0" > $STATEFILE
exit 0
