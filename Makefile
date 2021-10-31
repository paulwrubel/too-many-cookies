.PHONY: run clean

PYTHON_COMMAND=python3

MAIN_FILE=tmc.py

CONFIG_FILE=config.yaml
SAVE_FILE=save.txt

all: run

run: clean $(STATE_FILE)
	$(PYTHON_COMMAND) $(MAIN_FILE) $(CONFIG_FILE) $(SAVE_FILE)