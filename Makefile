all: frag_mm_meta fragment_context
	
frag_mm_meta:
	$(MAKE) -C contexts/media

fragment_context:
	$(MAKE) -C contexts/fragment

.PHONY: clean frag_mm_meta fragment_context

clean:
	$(MAKE) -C contexts/media clean
	$(MAKE) -C contexts/fragment clean

