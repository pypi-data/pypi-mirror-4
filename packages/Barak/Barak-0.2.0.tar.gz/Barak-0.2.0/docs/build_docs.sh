rm -rf generated
rm -rf _build
mkdir -p generated
./make_index.py
make html
# git co gh-pages
# cd ..; /bin/cp -r docs/_build/html/* .;  git st
# git add generated _modules _static _sources *html _images searchindex.js objects.inv
# git ci -m'doc build'; git push
# git co master
