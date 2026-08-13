PYTHON ?= python3

POC0_SPECIFICATION := examples/hello/specification.json
POC0_SPECIR := examples/hello/hello.specir.json
POC0_BUILD_DIR := build/poc0
POC0 := prototypes/poc0/spec2exec_poc0.py

POC1_SPECIFICATION := examples/bounded-arithmetic/specification.json
POC1_SPECIR := examples/bounded-arithmetic/safe_add.specir.json
POC1_BUILD_DIR := build/poc1
POC1 := prototypes/poc1/spec2exec_poc1.py

.PHONY: verify lower build run poc0 poc1 poc1-verify test test-poc0 test-poc1 clean

verify:
	$(PYTHON) $(POC0) verify $(POC0_SPECIR) --specification $(POC0_SPECIFICATION) --evidence $(POC0_BUILD_DIR)/verification.json

lower:
	$(PYTHON) $(POC0) lower $(POC0_SPECIR) --specification $(POC0_SPECIFICATION) -o $(POC0_BUILD_DIR)/generated.c --evidence $(POC0_BUILD_DIR)/verification.json

build:
	$(PYTHON) $(POC0) build $(POC0_SPECIR) --specification $(POC0_SPECIFICATION) --build-dir $(POC0_BUILD_DIR)

run: build
	$(PYTHON) $(POC0) run $(POC0_SPECIR) --specification $(POC0_SPECIFICATION) $(POC0_BUILD_DIR)/hello

poc0:
	$(PYTHON) $(POC0) all $(POC0_SPECIR) --specification $(POC0_SPECIFICATION) --build-dir $(POC0_BUILD_DIR)

poc1-verify:
	$(PYTHON) $(POC1) verify $(POC1_SPECIR) --specification $(POC1_SPECIFICATION)

poc1:
	$(PYTHON) $(POC1) all $(POC1_SPECIR) --specification $(POC1_SPECIFICATION) --build-dir $(POC1_BUILD_DIR)

test-poc0:
	$(PYTHON) -m unittest discover -s tests/poc0 -p 'test_*.py' -v

test-poc1:
	$(PYTHON) -m unittest discover -s tests/poc1 -p 'test_*.py' -v

test: test-poc0 test-poc1

clean:
	rm -rf build
