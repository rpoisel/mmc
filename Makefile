WORK_DIR=/tmp
PROG_NAME=mmc
VERSION=0.9
SUB_VER=-3
LD_LIBRARY_PATH_64 := "collating/fragment:collating/magic/lib/magic/linux-x86_64"
LD_LIBRARY_PATH_32 := "collating/fragment:collating/magic/lib/magic/linux-i686"

SVN=/usr/bin/svn
SVN_FLAGS=--force
TAR=/bin/tar
RM=/bin/rm
MV=/bin/mv
RM_FLAGS=-rf
PYTHON=/usr/bin/python
PYINSTALLER=/usr/local/pyinstaller/pyinstaller.py
PYINSTALLER_FLAGS=--onefile -o

DIR_FRAGMENT_CONTEXT=collating/fragment
DIR_BUILD=build
DIR_DIST=dist
DIR_DIST_STATIC=/tmp/mmc

all: fragment_context 
	
fragment_context:
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) -f Makefile_lnx.mk

.PHONY: clean fragment_context

deb:
	$(SVN) export $(SVN_FLAGS) ../trunk $(WORK_DIR)/$(PROG_NAME)-$(VERSION)$(SUB_VER)
	(cd $(WORK_DIR) && $(TAR) -czvf $(PROG_NAME)-$(VERSION)$(SUB_VER).tar.gz $(PROG_NAME)-$(VERSION)$(SUB_VER))
	(cd $(WORK_DIR) && $(TAR) -czvf $(PROG_NAME)_$(VERSION).orig.tar.gz $(PROG_NAME)-$(VERSION)$(SUB_VER))
	(cd $(WORK_DIR)/$(PROG_NAME)-$(VERSION)$(SUB_VER) && debuild -uc -us)

static64: 
	(export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH_64) && $(MAKE) static_all)

static32: 
	(export LD_LIBRARY_PATH=$(LD_LIBRARY_PATH_32) && $(MAKE) static_all)

static_all: fragment_context
	-$(RM) $(RM_FLAGS) $(DIR_DIST_STATIC)/$(PROG_NAME)-$(VERSION)$(SUB_VER)
	$(PYTHON) $(PYINSTALLER) $(PYINSTALLER_FLAGS) $(DIR_DIST_STATIC) mmc.py
	$(SVN) export $(SVN_FLAGS) data $(DIR_DIST_STATIC)/dist/data
	-$(RM) $(RM_FLAGS) $(DIR_DIST_STATIC)/dist/data/frags_ref
	-(for i in animation jpeg png; do $(RM) $(RM_FLAGS) $(DIR_DIST_STATIC)/dist/data/magic/$$i ; done)
	$(MV) $(DIR_DIST_STATIC)/dist $(DIR_DIST_STATIC)/$(PROG_NAME)-$(VERSION)$(SUB_VER)
	$(TAR) -cjpf /tmp/$(PROG_NAME)-$(VERSION)$(SUB_VER).tar.bz2 -C $(DIR_DIST_STATIC) $(PROG_NAME)-$(VERSION)$(SUB_VER)

debclean:
	-rm -rf $(WORK_DIR)/$(PROG_NAME)*

clean:
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) -f Makefile_lnx.mk clean
	-$(RM) $(RM_FLAGS) $(DIR_DIST_STATIC)
	-$(RM) $(RM_FLAGS) $(DIR_BUILD) $(DIR_DIST)
	-$(RM) $(RM_FLAGS) logdict*
