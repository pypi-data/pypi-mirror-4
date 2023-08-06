
html: api.txt anchors outputs
	asciidoc -v -b html -d article -n -a toc api.txt

pdf: api.txt anchors outputs
	a2x -k -a toc -L -d article -f pdf -v --dblatex-opts "-P latex.output.revhistory=0 -P doc.collab.show=1 -P   toc.section.depth=2" api.txt

epub: api.txt anchors outputs
	export XML_CATALOG_FILES=export XML_CATALOG_FILES="catalog.xml"; a2x -L -f epub -d article --verbose --   xsltproc-opts "--stringparam toc.section.depth 2 --stringparam generate.section.toc.level 1" api.txt

all: html pdf epub

anchors:
	python include_anchors.py api.txt

outputs:
	coopr api --asciidoc > coopr_api.txt


Xpdf: api.txt anchors
	a2x -a toc -a docinfo -k -L -dbook -f pdf -v --dblatex-opts "-P latex.output.revhistory=0 -P doc.collab.show=1 -P toc.section.depth=10" --asciidoc-opts=--conf-file=latex.conf api.txt

Xhtml: api.txt anchors
	#a2x -a latexmath -a docinfo -k -L -d book -f xhtml -v --asciidoc-opts=--conf-file=html.conf api.txt
	asciidoc -v -b html -d book -n -a toc -a latexmath -f html.conf -v api.txt
	#a2x -a toc -a docinfo -k -L -dbook -f xhtml -v --asciidoc-opts=--conf-file=latex.conf api.txt

Xepub: api.txt anchors
	export XML_CATALOG_FILES=export XML_CATALOG_FILES="catalog.xml"; a2x -a docinfo -f epub -d book --verbose --xsltproc-opts "--stringparam toc.section.depth 10 --stringparam generate.section.toc.level 1" api.txt

clean:
	- \rm api.xml

