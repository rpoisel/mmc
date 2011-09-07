WORK_DIR=/tmp
PROG_NAME=mmc
VERSION=-0.8
#SUB_VER=-1
SUB_VER=

all: fragment_context 
#all: frag_mm_meta fragment_context 

DIR_FRAG_MM_META=collating/media
DIR_FRAGMENT_CONTEXT=collating/fragment
	
frag_mm_meta:
	$(MAKE) -C $(DIR_FRAG_MM_META)

fragment_context:
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT)

.PHONY: clean fragment_context
#.PHONY: clean fragment_context frag_mm_meta

deb:
	svn export ../trunk $(WORK_DIR)/$(PROG_NAME)$(VERSION)$(SUB_VER)
	(cd $(WORK_DIR) && tar -czvf $(PROG_NAME)$(VERSION)$(SUB_VER).tar.gz $(PROG_NAME)$(VERSION)$(SUB_VER))
	-(cd $(WORK_DIR)/$(PROG_NAME)$(VERSION)$(SUB_VER) && dh_make -e rpoisel@fhstp.ac.at -c lgpl3 -s -f ../$(PROG_NAME)$(VERSION)$(SUB_VER).tar.gz)
	(cd $(WORK_DIR)/$(PROG_NAME)$(VERSION)$(SUB_VER) && debuild -uc -us)

debclean:
	-rm -rf $(WORK_DIR)/$(PROG_NAME)*

clean:
	$(MAKE) -C $(DIR_FRAG_MM_META) clean
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) clean
