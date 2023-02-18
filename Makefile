ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

# Build Hugo website
.PHONY: build
build:
	docker run --rm -it -v $(PWD)/website:/src -v $(PWD)/docs:/docs klakegg/hugo:ext-alpine

# Run Hugo server
.PHONY: run
run:
	docker run --rm -it -v $(PWD)/website:/src -v $(PWD)/docs:/docs -p 1313:1313 klakegg/hugo:ext-alpine server
