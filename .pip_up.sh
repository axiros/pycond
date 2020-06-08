#!/usr/bin/env bash

expl='
Change the version in .README.md.tmpl - not in the generated one before calling this.

We have to commit once before setting links, in order to have the hash pointing to the blob with that checksum:
e.g. such a link can then be generated:
[mdtool.py]: https://github.com/axiros/pytest2md/blob/bf37bbb1302553d8732713b2ebfb415b27c0616c/pytest2md/mdtool.py
'

echo "Uploading to pip"
set -x
here="$(unset CDPATH && cd "$(dirname "${BASH_SOURCE[0]}")" && echo "$PWD")"
cd "$here" || exit 1
#export NOLINKREPL=true
export MD_LINKS_FOR=github
pytest tests || exit 1
git commit --amend -am 'links auto replaced'
#unset NOLINKREPL
#git commit -am 'pre_pypi_upload' # to have the commit hash for the links
#slt="https://github.com/axiros/DevApps/blob/`git rev-parse  HEAD`"
#slt="$slt/%(file)s%(#Lline)s"
#echo "Setting links..."
#mdtool set_links src_link_tmpl="github" md_file="README.md"
git push

clean () {
    rm -rf ./dist
    rm -rf ./pytest2md.egg-info
    rm -rf ./build
}
clean
python setup.py clean sdist bdist_wheel
twine upload ./dist/*
clean







