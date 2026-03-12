PROJECT_DIR := $(shell pwd)
VENV        := $(PROJECT_DIR)/.venv
UNAME       := $(shell uname -s)
HAS_INSTALLEX := $(shell command -v installex 2>/dev/null && echo 1 || echo 0)

ifeq ($(UNAME),Darwin)
  INSTALL_DIR := $(HOME)/.local/bin
else ifeq ($(HAS_INSTALLEX),1)
  INSTALL_DIR := $(HOME)/.services/cli
else
  INSTALL_DIR := $(HOME)/.local/bin
endif

WRAPPER     := $(INSTALL_DIR)/ppt-cli

.PHONY: install uninstall help

define write_wrapper
	@mkdir -p "$(INSTALL_DIR)"
	@printf '#!/bin/sh\nexport USER_ORIGINAL_CWD="$$PWD"\ncd "$(PROJECT_DIR)" || exit 1\nexec python3 "$(PROJECT_DIR)/ppt-cli.py" "$$@"\n' > "$(WRAPPER)"
	@chmod +x "$(WRAPPER)"
endef

install: $(VENV)
ifeq ($(HAS_INSTALLEX),1)
  ifneq ($(UNAME),Darwin)
	@installex "$(PROJECT_DIR)/ppt-cli.py" --install-dir "$(INSTALL_DIR)" --wrap --cwd "$(PROJECT_DIR)"
  else
	$(write_wrapper)
  endif
else
	$(write_wrapper)
endif
	@echo "Installed: ppt-cli → $(WRAPPER)"
	@case "$$PATH" in *$(INSTALL_DIR)*) ;; *) echo "NOTE: Add $(INSTALL_DIR) to your PATH:" && echo "  export PATH=\"$(INSTALL_DIR):\$$PATH\"" ;; esac

$(VENV):
	@echo "Creating venv and installing dependencies..."
	@python3 -m venv $(VENV)
	@$(VENV)/bin/pip install --quiet python-pptx
	@echo "venv ready"

uninstall:
ifeq ($(HAS_INSTALLEX),1)
  ifneq ($(UNAME),Darwin)
	@installex --remove ppt-cli --install-dir "$(INSTALL_DIR)" || true
  else
	@rm -f "$(WRAPPER)"
  endif
else
	@rm -f "$(WRAPPER)"
endif
	@echo "Uninstalled: ppt-cli"

help:
	@echo "Targets:"
	@echo "  install    Create venv, install deps, install ppt-cli to $(INSTALL_DIR)"
	@echo "  uninstall  Remove ppt-cli"
	@echo ""
	@echo "Optional system deps (for screenshot command):"
ifeq ($(UNAME),Darwin)
	@echo "  brew install --cask libreoffice   Renders slides to PDF"
	@echo "  brew install poppler              Converts PDF pages to PNG (pdftoppm)"
else
	@echo "  libreoffice     Renders slides to PDF"
	@echo "  poppler-utils   Converts PDF pages to PNG (pdftoppm)"
endif
	@echo ""
	@echo "Ensure $(INSTALL_DIR) is in your PATH"
