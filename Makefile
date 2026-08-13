PYTHON ?= python3
SPECIFICATION := examples/hello/specification.json
SPECIR := examples/hello/hello.specir.json
BUILD_DIR := build/poc0
POC0 := prototypes/poc0/spec2exec_poc0.py

.PHONY: verify lower build run poc0 test clean

verify:
	$(PYTHON) $(POC0) verify $(SPECIR) --specification $(SPECIFICATION) --evidence $(BUILD_DIR)/verification.json

lower:
	$(PYTHON) $(POC0) lower $(SPECIR) --specification $(SPECIFICATION) -o $(BUILD_DIR)/generated.c --evidence $(BUILD_DIR)/verification.json

build:
	$(PYTHON) $(POC0) build $(SPECIR) --specification $(SPECIFICATION) --build-dir $(BUILD_DIR)

run: build
	$(PYTHON) $(POC0) run $(SPECIR) --specification $(SPECIFICATION) $(BUILD_DIR)/hello

poc0:
	$(PYTHON) $(POC0) all $(SPECIR) --specification $(SPECIFICATION) --build-dir $(BUILD_DIR)

test:
	$(PYTHON) -m unittest discover -s tests/poc0 -p 'test_*.py' -v

clean:
	rm -rf build
