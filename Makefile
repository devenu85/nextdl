all: nextdl README.md CONTRIBUTING.md README.txt nextdl.1 nextdl.bash-completion nextdl.zsh nextdl.fish supportedsites

clean:
	rm -rf nextdl.1.temp.md nextdl.1 nextdl.bash-completion README.txt MANIFEST build/ dist/ .coverage cover/ nextdl.tar.gz nextdl.zsh nextdl.fish nextdl/extractor/lazy_extractors.py *.dump *.part* *.nextdl *.info.json *.mp4 *.m4a *.flv *.mp3 *.avi *.mkv *.webm *.3gp *.wav *.ape *.swf *.jpg *.png CONTRIBUTING.md.tmp nextdl nextdl.exe
	find . -name "*.pyc" -delete
	find . -name "*.class" -delete

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python

# set SYSCONFDIR to /etc if PREFIX=/usr or PREFIX=/usr/local
SYSCONFDIR = $(shell if [ $(PREFIX) = /usr -o $(PREFIX) = /usr/local ]; then echo /etc; else echo $(PREFIX)/etc; fi)

# set markdown input format to "markdown-smart" for pandoc version 2 and to "markdown" for pandoc prior to version 2
MARKDOWN = $(shell if [ `pandoc -v | head -n1 | cut -d" " -f2 | head -c1` = "2" ]; then echo markdown-smart; else echo markdown; fi)

install: nextdl nextdl.1 nextdl.bash-completion nextdl.zsh nextdl.fish
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 nextdl $(DESTDIR)$(BINDIR)
	install -d $(DESTDIR)$(MANDIR)/man1
	install -m 644 nextdl.1 $(DESTDIR)$(MANDIR)/man1
	install -d $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	install -m 644 nextdl.bash-completion $(DESTDIR)$(SYSCONFDIR)/bash_completion.d/nextdl
	install -d $(DESTDIR)$(SHAREDIR)/zsh/site-functions
	install -m 644 nextdl.zsh $(DESTDIR)$(SHAREDIR)/zsh/site-functions/_nextdl
	install -d $(DESTDIR)$(SYSCONFDIR)/fish/completions
	install -m 644 nextdl.fish $(DESTDIR)$(SYSCONFDIR)/fish/completions/nextdl.fish

codetest:
	flake8 .

test:
	#nosetests --with-coverage --cover-package=nextdl --cover-html --verbose --processes 4 test
	nosetests --verbose test
	$(MAKE) codetest

ot: offlinetest

# Keep this list in sync with devscripts/run_tests.sh
offlinetest: codetest
	$(PYTHON) -m nose --verbose test \
		--exclude test_age_restriction.py \
		--exclude test_download.py \
		--exclude test_iqiyi_sdk_interpreter.py \
		--exclude test_socks.py \
		--exclude test_subtitles.py \
		--exclude test_write_annotations.py \
		--exclude test_youtube_lists.py \
		--exclude test_youtube_signature.py

tar: nextdl.tar.gz

.PHONY: all clean install test tar bash-completion pypi-files zsh-completion fish-completion ot offlinetest codetest supportedsites

pypi-files: nextdl.bash-completion README.txt nextdl.1 nextdl.fish

nextdl: nextdl/*.py nextdl/*/*.py
	mkdir -p zip
	for d in nextdl nextdl/downloader nextdl/extractor nextdl/postprocessor ; do \
	  mkdir -p zip/$$d ;\
	  cp -pPR $$d/*.py zip/$$d/ ;\
	done
	touch -t 200001010101 zip/nextdl/*.py zip/nextdl/*/*.py
	mv zip/nextdl/__main__.py zip/
	cd zip ; zip -q ../nextdl nextdl/*.py nextdl/*/*.py __main__.py
	rm -rf zip
	echo '#!$(PYTHON)' > nextdl
	cat nextdl.zip >> nextdl
	rm nextdl.zip
	chmod a+x nextdl

README.md: nextdl/*.py nextdl/*/*.py
	COLUMNS=80 $(PYTHON) nextdl/__main__.py --help | $(PYTHON) devscripts/make_readme.py

CONTRIBUTING.md: README.md
	$(PYTHON) devscripts/make_contributing.py README.md CONTRIBUTING.md

issuetemplates: devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/1_broken_site.md .github/ISSUE_TEMPLATE_tmpl/2_site_support_request.md .github/ISSUE_TEMPLATE_tmpl/3_site_feature_request.md .github/ISSUE_TEMPLATE_tmpl/4_bug_report.md .github/ISSUE_TEMPLATE_tmpl/5_feature_request.md nextdl/version.py
	$(PYTHON) devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/1_broken_site.md .github/ISSUE_TEMPLATE/1_broken_site.md
	$(PYTHON) devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/2_site_support_request.md .github/ISSUE_TEMPLATE/2_site_support_request.md
	$(PYTHON) devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/3_site_feature_request.md .github/ISSUE_TEMPLATE/3_site_feature_request.md
	$(PYTHON) devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/4_bug_report.md .github/ISSUE_TEMPLATE/4_bug_report.md
	$(PYTHON) devscripts/make_issue_template.py .github/ISSUE_TEMPLATE_tmpl/5_feature_request.md .github/ISSUE_TEMPLATE/5_feature_request.md

supportedsites:
	$(PYTHON) devscripts/make_supportedsites.py docs/supportedsites.md

README.txt: README.md
	pandoc -f $(MARKDOWN) -t plain README.md -o README.txt

nextdl.1: README.md
	$(PYTHON) devscripts/prepare_manpage.py nextdl.1.temp.md
	pandoc -s -f $(MARKDOWN) -t man nextdl.1.temp.md -o nextdl.1
	rm -f nextdl.1.temp.md

nextdl.bash-completion: nextdl/*.py nextdl/*/*.py devscripts/bash-completion.in
	$(PYTHON) devscripts/bash-completion.py

bash-completion: nextdl.bash-completion

nextdl.zsh: nextdl/*.py nextdl/*/*.py devscripts/zsh-completion.in
	$(PYTHON) devscripts/zsh-completion.py

zsh-completion: nextdl.zsh

nextdl.fish: nextdl/*.py nextdl/*/*.py devscripts/fish-completion.in
	$(PYTHON) devscripts/fish-completion.py

fish-completion: nextdl.fish

lazy-extractors: nextdl/extractor/lazy_extractors.py

_EXTRACTOR_FILES = $(shell find nextdl/extractor -iname '*.py' -and -not -iname 'lazy_extractors.py')
nextdl/extractor/lazy_extractors.py: devscripts/make_lazy_extractors.py devscripts/lazy_load_template.py $(_EXTRACTOR_FILES)
	$(PYTHON) devscripts/make_lazy_extractors.py $@

nextdl.tar.gz: nextdl README.md README.txt nextdl.1 nextdl.bash-completion nextdl.zsh nextdl.fish ChangeLog AUTHORS
	@tar -czf nextdl.tar.gz --transform "s|^|nextdl/|" --owner 0 --group 0 \
		--exclude '*.DS_Store' \
		--exclude '*.kate-swp' \
		--exclude '*.pyc' \
		--exclude '*.pyo' \
		--exclude '*~' \
		--exclude '__pycache__' \
		--exclude '.git' \
		--exclude 'docs/_build' \
		-- \
		bin devscripts test nextdl docs \
		ChangeLog AUTHORS LICENSE README.md README.txt \
		Makefile MANIFEST.in nextdl.1 nextdl.bash-completion \
		nextdl.zsh nextdl.fish setup.py setup.cfg \
		nextdl
