WORK_DIR=/tmp
PROG_NAME=mmc
VERSION=0.9
SUB_VER=-3

all: fragment_context 
#all: frag_mm_meta fragment_context 

DIR_FRAG_MM_META=collating/media
DIR_FRAGMENT_CONTEXT=collating/fragment
DIR_BUILD=build
DIR_DIST=dist
	
frag_mm_meta:
	$(MAKE) -C $(DIR_FRAG_MM_META)

fragment_context:
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) -f Makefile_lnx.mk

.PHONY: clean fragment_context
#.PHONY: clean fragment_context frag_mm_meta

deb:
	svn export --force ../trunk $(WORK_DIR)/$(PROG_NAME)-$(VERSION)$(SUB_VER)
	(cd $(WORK_DIR) && tar -czvf $(PROG_NAME)-$(VERSION)$(SUB_VER).tar.gz $(PROG_NAME)-$(VERSION)$(SUB_VER))
	(cd $(WORK_DIR) && tar -czvf $(PROG_NAME)_$(VERSION).orig.tar.gz $(PROG_NAME)-$(VERSION)$(SUB_VER))
	(cd $(WORK_DIR)/$(PROG_NAME)-$(VERSION)$(SUB_VER) && debuild -uc -us)

debclean:
	-rm -rf $(WORK_DIR)/$(PROG_NAME)*

clean:
	$(MAKE) -C $(DIR_FRAG_MM_META) clean
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) -f Makefile_lnx.mk clean
	-rm -rf $(DIR_BUILD) $(DIR_DIST)
