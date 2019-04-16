###############################################################################
# CONFIGURATION                                                               #
###############################################################################

PROJECT_DIR = '{{ cookiecutter.project_path }}'
PROJECT_MEDIA = '{{ cookiecutter.media_path }}'
POST_ASSET_TAG = '{{ cookiecutter.asset_prefix }}'
POST_IMAGE = '{{ cookiecutter.post_icon_image }}'

PYTHON = {{ cookiecutter.python_interpreter }}
PKG_MGR = {{ cookiecutter.package_manager }}


###############################################################################
# SETUP                                                                       #
###############################################################################

SUBDIR_ROOTS := posts media publish
DIRS := . $(shell find $(SUBDIR_ROOTS) -type d)
GARBAGE_PATTERNS := *.pyc *~ *-checkpoint.ipynb *.backup
GARBAGE := $(foreach DIR,$(DIRS),$(addprefix $(DIR)/,$(GARBAGE_PATTERNS)))

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

###############################################################################
# COMMANDS                                                                    #
###############################################################################
.PHONY: help setup teardown all \
		venv-create venv-remove \
        requirements requirements-generate \
        clean clean-garbage clean-publish clean-media \
		media media-copy \
		publish

.DEFAULT-GOAL := help

help: ## Displays this help message
	@printf 'Usage: make \033[36m[target]\033[0m\n'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ''

setup: venv-create requirements ## Sets up the environment

teardown: venv-remove ## Removes the environment

all: clean media-copy publish ## Runs the entire process to generate publish files

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

clean: clean-garbage clean-publish ## Cleans up all project files

clean-garbage: ## Delete all garbage Python files or temp files
	@printf "[INFO] Cleaning garbage files... "
	@rm -rf $(GARBAGE)
	@printf "DONE.\n"

clean-media:  ## Cleans out the media files
	@printf "[INFO] Cleaning media files... "
	@rm media/dynamic/* || true
	@printf "DONE.\n"

clean-publish: ## Cleans all the files related to publishing
	@printf "[INFO] Cleaning publish directory... "
	@$(PYTHON) src/publish.py clean
	@printf "DONE.\n"

# Media

media: clean-media media-copy ## Cleans then copies over media files from the project directory

media-copy:  ## Copies media files from project directory
	@printf "[INFO] Copying media files from project... "
	@cp $(PROJECT_DIR)/$(PROJECT_MEDIA)/* media/dynamic/
	@printf "DONE.\n"

# Publishing

publish: ## Generates the final post and media for the post to upload
	@printf "[INFO] Creating final post... "
	@$(PYTHON) src/publish.py create $(FINAL_POST) --post-image media/$(POST_IMAGE) --asset-tag $(POST_ASSET_TAG)
	@printf "DONE.\n"
