# PYSAMMSNMP package
This package allows for SNMP querying and command execution

# To build deb package
`docker run -it --rm -v $(pwd):/usr/src samm-repo /usr/local/bin/build-deb.sh`

# To update repository
`package=<package deb file>
docker run --rm -it -v $(pwd):/usr/src -w /usr/src samm-repo /usr/local/bin/add-file-repo.sh $package jammy`
