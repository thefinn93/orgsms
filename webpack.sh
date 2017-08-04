#!/bin/sh
set -ex
mkdir -p orgsms/static/vendor
for package in moment socket.io-client; do
  mkdir -p orgsms/static/vendor/$package
  if [ -d node_modules/$package/dist ]; then
    cp -vr node_modules/$package/dist/* orgsms/static/vendor/$package/
  fi

  if [ -d node_modules/$package/min ]; then
    cp -vr node_modules/$package/min/* orgsms/static/vendor/$package/
  fi
done
