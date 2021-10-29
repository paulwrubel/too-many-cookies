.PHONY: run clean

PYTHON_COMMAND=python3

MAIN_FILE=tmc.py
STATE_FILE=state.yaml

all: run

run: clean $(STATE_FILE)
	$(PYTHON_COMMAND) $(MAIN_FILE) $(STATE_FILE)

clean: