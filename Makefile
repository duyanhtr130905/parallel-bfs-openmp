ifeq ($(origin CC), default)
CC = gcc
endif
PYTHON ?= python
CPPFLAGS += -Iinclude
CFLAGS ?= -O2 -Wall -Wextra -Wpedantic
CFLAGS += -std=c11 -fopenmp
LDLIBS += -fopenmp
EXEEXT :=
ifeq ($(OS),Windows_NT)
EXEEXT := .exe
endif
BIN := build/bfs$(EXEEXT)

.PHONY: all build test test-bfs check-scaffold check-api check-openmp report clean help
all: build
build: $(BIN)
$(BIN): src/main.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/main.c $(LDFLAGS) $(LDLIBS) -o $(BIN)
check-scaffold:
	$(PYTHON) scripts/check_scaffold.py
check-api:
	$(CC) $(CPPFLAGS) $(CFLAGS) -Werror -fsyntax-only tests/api_contract.c
test: build check-scaffold check-api test-tools
	$(PYTHON) tests/test_cli.py --binary $(BIN)
	$(PYTHON) tests/test_clean.py
test-bfs:
	$(PYTHON) -c "import sys; sys.exit('NOT IMPLEMENTED: BFS correctness tests await real modules.')"
check-openmp:
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CFLAGS) tests/openmp_probe.c $(LDFLAGS) $(LDLIBS) -o build/openmp_probe$(EXEEXT)
	./build/openmp_probe$(EXEEXT) --strict
	$(PYTHON) tests/test_openmp_probe.py build/openmp_probe$(EXEEXT)
report:
	cd report && xelatex -interaction=nonstopmode -halt-on-error main.tex
	cd report && bibtex main
	cd report && xelatex -interaction=nonstopmode -halt-on-error main.tex
	cd report && xelatex -interaction=nonstopmode -halt-on-error main.tex
clean:
	$(PYTHON) scripts/clean.py
help:
	@echo "build: bootstrap CLI; test: CLI + scaffold/API + test-tools; test-bfs: unavailable"
	@echo "check-scaffold; check-openmp; report: XeLaTeX + BibTeX; clean: known outputs"

.PHONY: test-tools
test-tools:
	$(PYTHON) -m unittest discover -s tests -p test_experiment_tools.py -v
