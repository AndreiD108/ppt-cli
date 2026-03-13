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

.PHONY: install uninstall test clean clean-cache check help

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

clean:
	@rm -rf dist/ build/ ppt_cli.egg-info/
	@echo "Removed dist/, build/, ppt_cli.egg-info/"

clean-cache:
	@rm -rf /tmp/ppt-cli /tmp/ppt-cli-screenshots
	@echo "Removed /tmp/ppt-cli and /tmp/ppt-cli-screenshots"

check:
	@echo "=== ppt-cli environment check ==="
	@echo ""
	@echo "— LibreOffice (for screenshot command):"
	@if command -v libreoffice >/dev/null 2>&1; then \
		echo "  ✓ libreoffice found: $$(command -v libreoffice)"; \
	else \
		echo "  ✗ libreoffice not found"; \
		echo "    Install: sudo apt install libreoffice  (Linux)"; \
		echo "             brew install --cask libreoffice  (macOS)"; \
	fi
	@echo ""
	@echo "— pdftoppm (for screenshot command):"
	@if command -v pdftoppm >/dev/null 2>&1; then \
		echo "  ✓ pdftoppm found: $$(command -v pdftoppm)"; \
	else \
		echo "  ✗ pdftoppm not found"; \
		echo "    Install: sudo apt install poppler-utils  (Linux)"; \
		echo "             brew install poppler  (macOS)"; \
	fi
	@echo ""
	@echo "— GEMINI_API_KEY (for add-image --prompt and image-gen):"
	@if [ -n "$$GEMINI_API_KEY" ]; then \
		echo "  ✓ GEMINI_API_KEY is set"; \
	else \
		echo "  ✗ GEMINI_API_KEY not set"; \
		echo "    Get one at: https://aistudio.google.com/api-keys"; \
		echo "    Then: export GEMINI_API_KEY=\"your-key\""; \
	fi

help:
	@echo "Targets:"
	@echo "  install      Create venv, install deps, install ppt-cli"
	@echo "  uninstall    Remove ppt-cli"
	@echo "  test         Run test suite"
	@echo "  check        Check optional dependencies (libreoffice, GEMINI_API_KEY)"
	@echo "  clean-cache  Remove /tmp staging dirs and screenshot cache"
	@echo ""
	@echo "Optional dependencies:"
	@echo "  libreoffice + poppler   For the screenshot command"
	@echo "  GEMINI_API_KEY          For AI image generation (add-image --prompt, image-gen)"
	@echo "                          Get one at: https://aistudio.google.com/api-keys"
	@echo ""
	@echo "Run 'make check' to verify your environment."
ifdef INSTALL_DIR
	@echo ""
	@echo "Ensure $(INSTALL_DIR) is in your PATH"
endif
