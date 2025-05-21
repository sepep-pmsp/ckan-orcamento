#!/usr/bin/env bash
set -e

echo "Installing ckanext-seplan"
pip install -e /srv/app/src_extensions/ckanext-seplan

echo "Adding ckanext-seplan to CKAN__PLUGINS"
export CKAN__PLUGINS="$CKAN__PLUGINS seplan"
