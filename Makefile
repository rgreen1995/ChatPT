.PHONY: test format lint all version bump-version clean-dist build publish install

# Commands
POETRY := poetry
PYTEST := $(POETRY) run pytest
TWINE := $(POETRY) run twine
RUFF  := $(POETRY) run ruff
# Source directories
SRC_DIR := chat_pt
APP_DIR := app.py
TESTS_DIR := tests
# Default test command for all tests
test:
	$(PYTEST) $(TESTS_DIR)

# Pattern rule to test specific modules
test-%:
	$(PYTEST) $(TESTS_DIR)/$*

format:
	$(RUFF) format $(SRC_DIR) $(TESTS_DIR) app.py
	$(RUFF) check --fix  $(SRC_DIR) $(TESTS_DIR) app.py

check-format:
	$(RUFF) check $(SRC_DIR) $(TESTS_DIR) app.py
	$(RUFF) format --check $(SRC_DIR) $(TESTS_DIR) app.py

# Update the version
bump-version:
	$(POETRY) version patch  # or 'minor' or 'major', depending on the changes

all: format test
