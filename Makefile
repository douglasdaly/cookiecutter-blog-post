###############################################################################
# CONFIGURATION                                                               #
###############################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

PYTHON = python
PKG_MGR = pipenv


###############################################################################
# SETUP                                                                       #
###############################################################################

SUBDIR_ROOTS := docs src tests
DIRS := . $(shell find $(SUBDIR_ROOTS) -type d)
GARBAGE_PATTERNS := *.pyc *~ *-checkpoint.ipynb
GARBAGE := $(foreach DIR,$(DIRS),$(addprefix $(DIR)/,$(GARBAGE_PATTERNS)))

INVOKE = invoke
UNIT_TEST = pytest

ifeq ($(PKG_MGR), pipenv)
    RUN_PRE = pipenv run
	VENV_DIR := $(pipenv --venv)

	CREATE_VENV =
	REMOVE_VENV = pipenv --rm
    INSTALL_DEPENDENCIES = pipenv install --dev
    GENERATE_DEPENDENCIES = pipenv lock --dev -r > requirements.txt
else
    RUN_PRE =
	VENV_DIR = env

	CREATE_VENV := virtualenv $(VENV_DIR)/
	REMOVE_VENV := rm -rf $(VENV_DIR)
    INSTALL_DEPENDENCIES = pip install -r requirements.txt
    GENERATE_DEPENDENCIES = pip freeze --local > requirements.txt
endif

ACTIVATE_VENV := source $(VENV_DIR)/bin/activate
DEACTIVATE_VENV = deactivate

PYTHON := $(RUN_PRE) $(PYTHON)
INVOKE := $(RUN_PRE) $(INVOKE)
UNIT_TEST := $(RUN_PRE) $(UNIT_TEST)

###############################################################################
# COMMANDS                                                                    #
###############################################################################
.PHONY: help setup teardown \
		venv-create venv-remove \
        requirements requirements-generate \
        clean

.DEFAULT-GOAL := help

help: ## Displays this help message
	@printf 'Usage: make \033[36m[target]\033[0m\n'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ''

setup: venv-create requirements ## Sets up the environment for development

teardown: venv-remove ## Removes the environment for development

# Virtual environment

venv-create: ## Creates the virtual environment for this project
	$(CREATE_VENV)

venv-remove: ## Removes the virtual environment for this project
	$(REMOVE_VENV)

# Requirements

requirements: ## Installs Python dependencies
	$(INSTALL_DEPENDENCIES)

requirements-generate: ## Generates the project's requirements.txt file
	$(GENERATE_DEPENDENCIES)

# Cleaning

clean: ## Delete all compiled Python files or temp files
	@rm -rf $(GARBAGE)
