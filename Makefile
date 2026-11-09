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
PARALLEL_TEST_BIN := build/test_parallel$(EXEEXT)

.PHONY: all build test test-bfs test-parallel check-scaffold check-api check-openmp report clean help
all: build
build: $(BIN)
$(BIN): src/main.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/main.c $(LDFLAGS) $(LDLIBS) -o $(BIN)
$(PARALLEL_TEST_BIN): tests/test_parallel.c src/bfs_parallel_basic.c src/bfs_parallel_optimized.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_parallel.c src/bfs_parallel_basic.c src/bfs_parallel_optimized.c $(LDFLAGS) $(LDLIBS) -o $(PARALLEL_TEST_BIN)
test-parallel: $(PARALLEL_TEST_BIN)
	./$(PARALLEL_TEST_BIN)
check-scaffold:
	$(PYTHON) scripts/check_scaffold.py
check-api:
	$(CC) $(CPPFLAGS) $(CFLAGS) -Werror -fsyntax-only tests/api_contract.c
test: build check-scaffold check-api test-parallel
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
	@echo "build: bootstrap CLI; test: CLI + parallel BFS correctness checks"
	@echo "test-bfs: sequential correctness (A, not implemented yet); test-parallel: OpenMP BFS checks"
	@echo "check-scaffold; check-openmp; report: XeLaTeX + BibTeX; clean: known outputs"
