# Makefile for the Escacs Comtal Club website
# Uses Jekyll to build and serve the site locally with rbenv for Ruby version management

.PHONY: install build serve clean all setup rbenv-setup check-rbenv

# Default port for the Jekyll server
PORT ?= 4000

# Default environment
JEKYLL_ENV ?= development

# Ruby version to use
RUBY_VERSION ?= 3.4.8

all: setup install build serve

# Check if rbenv is installed
check-rbenv:
	@if ! command -v rbenv &> /dev/null; then \
		echo "rbenv not found. Please install rbenv first:"; \
		echo "For Debian/Ubuntu: sudo apt install rbenv"; \
		echo "For Arch/Manjaro: sudo pacman -S rbenv"; \
		echo "Then run: make rbenv-setup"; \
		exit 1; \
	fi

# Setup rbenv in shell
rbenv-setup:
	@echo "Setting up rbenv in your shell..."
	@grep -q 'rbenv init' ~/.zshrc || echo 'eval "$(rbenv init -)"' >> ~/.zshrc
	@echo "Please run: source ~/.zshrc"

# Setup Ruby environment
setup: check-rbenv
	@echo "Setting up Ruby environment..."
	@if ! rbenv versions | grep -q $(RUBY_VERSION); then \
		echo "Installing Ruby $(RUBY_VERSION)..."; \
		rbenv install $(RUBY_VERSION); \
	fi
	@echo "Setting local Ruby version to $(RUBY_VERSION)..."
	@rbenv local $(RUBY_VERSION)
	@echo "Rehashing rbenv to make new binaries available..."
	@rbenv rehash
	@echo "Installing bundler..."
	@eval "$$(rbenv init -)" && gem install bundler

# Create a marker file to track if gems need to be reinstalled
.gems_installed: Gemfile
	@echo "Installing dependencies..."
	@eval "$$(rbenv init -)" && bundle install
	@touch .gems_installed

# Install dependencies
install: setup .gems_installed

# Build the site
build: install
	@echo "Building site with Jekyll..."
	@eval "$$(rbenv init -)" && JEKYLL_ENV=$(JEKYLL_ENV) bundle exec jekyll build

# Serve the site locally
serve: install
	@echo "Starting local server on port $(PORT)..."
	@eval "$$(rbenv init -)" && bundle exec jekyll serve --livereload --port $(PORT)

# Build and immediately serve
build-serve: install
	@echo "Building and serving site..."
	@eval "$$(rbenv init -)" && JEKYLL_ENV=$(JEKYLL_ENV) bundle exec jekyll serve --livereload --port $(PORT)

# Clean build artifacts
clean:
	@echo "Cleaning up _site directory..."
	@rm -rf _site
	@rm -rf .jekyll-cache
	@rm -f .gems_installed
	@echo "Clean complete!"

# Help command
help:
	@echo "Makefile commands:"
	@echo "make rbenv-setup - Setup rbenv in your shell (run once)"
	@echo "make setup       - Setup Ruby environment with rbenv"
	@echo "make install     - Setup and install dependencies with bundle"
	@echo "make build       - Install dependencies and build the Jekyll site"
	@echo "make serve       - Install dependencies and serve the site locally with live reload"
	@echo "make build-serve - Install dependencies, build and immediately serve the site"
	@echo "make clean       - Remove generated files"
	@echo "make all         - Complete setup, install, build and serve"
	@echo ""
	@echo "Options:"
	@echo "PORT=4000           - Set custom port (default: 4000)"
	@echo "JEKYLL_ENV=production - Set Jekyll environment (default: development)"
	@echo "RUBY_VERSION=3.4.8    - Set Ruby version to use (default: 3.4.8)" 