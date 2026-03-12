PROJECT_DIR := $(shell pwd)
VENV        := $(PROJECT_DIR)/.venv
UNAME       := $(shell uname -s)
HAS_INSTALLEX := $(shell command -v installex >/dev/null 2>&1 && echo 1 || echo 0)

ifeq ($(UNAME),Darwin)
  INSTALL_DIR := $(HOME)/.local/bin
else ifneq ($(HAS_INSTALLEX),1)
  INSTALL_DIR := $(HOME)/.local/bin
endif

ifdef INSTALL_DIR
  WRAPPER := $(INSTALL_DIR)/ppt-cli
endif

.PHONY: install uninstall test clean-cache help

define write_wrapper
	@mkdir -p "$(INSTALL_DIR)"
	@printf '#!/bin/sh\nPYTHONPATH="$(PROJECT_DIR)" exec python3 -m ppt_cli "$$@"\n' > "$(WRAPPER)"
	@chmod +x "$(WRAPPER)"
endef

install: $(VENV)
ifeq ($(HAS_INSTALLEX),1)
  ifneq ($(UNAME),Darwin)
	@installex --exec 'env PYTHONPATH="$(PROJECT_DIR)" python3 -m ppt_cli' --name ppt-cli
  else
	$(write_wrapper)
	@echo "Installed: ppt-cli → $(WRAPPER)"
	@case "$$PATH" in *$(INSTALL_DIR)*) ;; *) echo "NOTE: Add $(INSTALL_DIR) to your PATH:" && echo "  export PATH=\"$(INSTALL_DIR):\$$PATH\"" ;; esac
  endif
else
	$(write_wrapper)
	@echo "Installed: ppt-cli → $(WRAPPER)"
	@case "$$PATH" in *$(INSTALL_DIR)*) ;; *) echo "NOTE: Add $(INSTALL_DIR) to your PATH:" && echo "  export PATH=\"$(INSTALL_DIR):\$$PATH\"" ;; esac
endif

$(VENV):
	@echo "Creating venv and installing dependencies..."
	@python3 -m venv $(VENV)
	@$(VENV)/bin/pip install --quiet -r requirements.txt
	@echo "venv ready"

test: $(VENV)
	@$(VENV)/bin/pytest tests/ -v

uninstall:
ifeq ($(HAS_INSTALLEX),1)
  ifneq ($(UNAME),Darwin)
	@installex --remove ppt-cli || true
  else
	@rm -f "$(WRAPPER)"
  endif
else
	@rm -f "$(WRAPPER)"
endif
	@echo "Uninstalled: ppt-cli"

clean-cache:
	@rm -rf /tmp/ppt-cli /tmp/ppt-cli-screenshots
	@echo "Removed /tmp/ppt-cli and /tmp/ppt-cli-screenshots"

help:
	@echo "Targets:"
	@echo "  install      Create venv, install deps, install ppt-cli"
	@echo "  uninstall    Remove ppt-cli"
	@echo "  test         Run test suite"
	@echo "  clean-cache  Remove /tmp staging dirs and screenshot cache"
	@echo ""
	@echo "Optional system deps (for screenshot command):"
ifeq ($(UNAME),Darwin)
	@echo "  brew install --cask libreoffice   Renders slides to PDF"
	@echo "  brew install poppler              Converts PDF pages to PNG (pdftoppm)"
else
	@echo "  libreoffice     Renders slides to PDF"
	@echo "  poppler-utils   Converts PDF pages to PNG (pdftoppm)"
endif
ifdef INSTALL_DIR
	@echo ""
	@echo "Ensure $(INSTALL_DIR) is in your PATH"
endif
