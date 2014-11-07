Convert mediwiki to markdown
============================

This script converts pages from a mysql database used by a mediawiki
installation to markdown pages using pandoc. It creates a git repository to
hold the pages and commits each revision with proper date and author
attribution.

Sample usage:

~~~
./convert.py --database freeon_wiki --user wikiuser --output-dir pages --password SECRET
~~~

The directory `pages` must not exist before running the script. After
completion, a git repository in `pages` will contain all page edits.
