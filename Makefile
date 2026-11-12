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
GRAPH_TEST := build/test_graph$(EXEEXT)
SERIAL_TEST := build/test_serial$(EXEEXT)
PARALLEL_TEST_BIN := build/test_parallel$(EXEEXT)

.PHONY: all build test test-bfs test-parallel check-scaffold check-api check-openmp report clean help
all: build
build: $(BIN)
$(BIN): src/main.c src/graph.c src/bfs_serial.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/main.c src/graph.c src/bfs_serial.c $(LDFLAGS) $(LDLIBS) -o $(BIN)
$(GRAPH_TEST): src/graph.c tests/test_graph.c include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/graph.c tests/test_graph.c $(LDFLAGS) $(LDLIBS) -o $(GRAPH_TEST)
$(SERIAL_TEST): src/graph.c src/bfs_serial.c tests/test_serial.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/graph.c src/bfs_serial.c tests/test_serial.c $(LDFLAGS) $(LDLIBS) -o $(SERIAL_TEST)
$(PARALLEL_TEST_BIN): tests/test_parallel.c src/graph.c src/bfs_serial.c src/bfs_parallel_basic.c src/bfs_parallel_optimized.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_parallel.c src/graph.c src/bfs_serial.c src/bfs_parallel_basic.c src/bfs_parallel_optimized.c $(LDFLAGS) $(LDLIBS) -o $(PARALLEL_TEST_BIN)
test-parallel: $(PARALLEL_TEST_BIN)
	./$(PARALLEL_TEST_BIN)
check-scaffold:
	$(PYTHON) scripts/check_scaffold.py
check-api:
	$(CC) $(CPPFLAGS) $(CFLAGS) -Werror -fsyntax-only tests/api_contract.c
test: build check-scaffold check-api test-bfs test-parallel test-tools test-cli-validation
	$(PYTHON) tests/test_cli.py --binary $(BIN)
	$(PYTHON) tests/test_clean.py
test-bfs: $(GRAPH_TEST) $(SERIAL_TEST)
	./$(GRAPH_TEST)
	./$(SERIAL_TEST)
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
	@echo "build: serial CLI; test: CLI + graph/serial + parallel correctness + tools"
	@echo "test-bfs: sequential correctness (A); test-parallel: OpenMP BFS checks (B)"
	@echo "check-scaffold; check-openmp; report: XeLaTeX + BibTeX; clean: known outputs"

.PHONY: test-tools
test-tools:
	$(PYTHON) -m unittest discover -s tests -p test_experiment_tools.py -v

.PHONY: test-cli-validation
test-cli-validation: build/test_cli_validation$(EXEEXT)
	./build/test_cli_validation$(EXEEXT)
build/test_cli_validation$(EXEEXT): tests/test_cli_validation.c src/main.c src/graph.c src/bfs_serial.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_cli_validation.c src/graph.c src/bfs_serial.c $(LDFLAGS) $(LDLIBS) -o $@
