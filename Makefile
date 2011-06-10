all: frag_mm_meta fragment_context 

DIR_FRAG_MM_META=collating/media
DIR_FRAGMENT_CONTEXT=collating/fragment
	
frag_mm_meta:
	$(MAKE) -C $(DIR_FRAG_MM_META)

fragment_context:
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT)

.PHONY: clean frag_mm_meta fragment_context

clean:
	$(MAKE) -C $(DIR_FRAG_MM_META) clean
	$(MAKE) -C $(DIR_FRAGMENT_CONTEXT) clean

