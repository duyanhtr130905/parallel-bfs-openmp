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

.PHONY: all build test test-bfs check-scaffold check-api check-openmp report clean help
all: build
build: $(BIN)
$(BIN): src/main.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/main.c $(LDFLAGS) $(LDLIBS) -o $(BIN)
$(GRAPH_TEST): src/graph.c tests/test_graph.c include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/graph.c tests/test_graph.c $(LDFLAGS) $(LDLIBS) -o $(GRAPH_TEST)
$(SERIAL_TEST): src/graph.c src/bfs_serial.c tests/test_serial.c include/bfs.h include/graph.h include/status.h
	$(PYTHON) -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
	$(CC) $(CPPFLAGS) $(CFLAGS) src/graph.c src/bfs_serial.c tests/test_serial.c $(LDFLAGS) $(LDLIBS) -o $(SERIAL_TEST)
check-scaffold:
	$(PYTHON) scripts/check_scaffold.py
check-api:
	$(CC) $(CPPFLAGS) $(CFLAGS) -Werror -fsyntax-only tests/api_contract.c
test: build check-scaffold check-api test-bfs
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
	@echo "build: bootstrap CLI; test: CLI and Role A correctness checks"
	@echo "check-scaffold; check-openmp; report: XeLaTeX + BibTeX; clean: known outputs"
