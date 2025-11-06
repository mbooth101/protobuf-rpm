#!/bin/bash

#################################
# downloads the sources of
# mysql-connector-python
# extracts them, removes the
# fonts since they have problematic
# copyright and packs the result
# under a new name
#################################

set -ex

NAME="mysql-connector-python"
# gets the version of the package from the spec file
VERSION=$( rpmspec -q --srpm --qf '%{VERSION}' "${NAME}.spec" )

# the source url of the mysql upstream tarball of the package
SOURCE_URL="http://dev.mysql.com/get/Downloads/Connector-python/8.0/${NAME}-${VERSION}-src.tar.gz"

# original archive name
OLD_ARCHIVE_NAME="${NAME}-${VERSION}-src"
# new tarball name, chnaged to able to differentiate between
# the original and the changed tarball
NEW_ARCHIVE_NAME="${OLD_ARCHIVE_NAME}-without-fonts"

# removes the old tarball, new tarball and the unpacked tarball
# if they are present in the current directory
rm -rf "./${OLD_ARCHIVE_NAME}.tar.gz" "./${OLD_ARCHIVE_NAME}/" "./${NEW_ARCHIVE_NAME}.tar.gz"

# downloads the source tarball from the url
# specified above
wget "${SOURCE_URL}"

#unpacks the original tarball
tar -xzf "${OLD_ARCHIVE_NAME}.tar.gz"

# removes the problematic font files
rm "./${OLD_ARCHIVE_NAME}/docs/mysqlx/_themes/sphinx_rtd_theme/static/css/fonts/"*

# compresses the modified sources under a new name
tar -czf "${NEW_ARCHIVE_NAME}.tar.gz" "${OLD_ARCHIVE_NAME}"

# removes the unpacked sources
rm -r "${OLD_ARCHIVE_NAME}"

# removes the original tarball so it isn't used
# by mistake
rm -f "${OLD_ARCHIVE_NAME}.tar.gz"
