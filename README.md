# PYSAMMSNMP package
This package allows for SNMP querying and command execution

# To build deb package
`docker run -it --rm -v $(pwd):/usr/src sammrepo /usr/local/bin/build-deb.sh`

# To update repository
`package=<package deb file>
arch=<architecture name arm64 or amd64>
docker run --rm -it -v $(pwd):/usr/src -v $(pwd)/../gpg:/gpg -v ~/.aws:/root/.aws -w /usr/src sammrepo /usr/local/bin/add-file-repo.sh $package jammy $arch`
