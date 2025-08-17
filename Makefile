#   ▄▄▄       ██▓ ██ ▄█▀ ▒█████  
#  ▒████▄    ▓██▒ ██▄█▒ ▒██▒  ██▒
#  ▒██  ▀█▄  ▒██▒▓███▄░ ▒██░  ██▒
#  ░██▄▄▄▄██ ░██░▓██ █▄ ▒██   ██░
#   ▓█   ▓██▒░██░▒██▒ █▄░ ████▓▒░
#   ▒▒   ▓▒█░░▓  ▒ ▒▒ ▓▒░ ▒░▒░▒░ 
#    ▒   ▒▒ ░ ▒ ░░ ░▒ ▒░  ░ ▒ ▒░ 
#    ░   ▒    ▒ ░░ ░░ ░ ░ ░ ░ ▒  
#        ░  ░ ▒ ░░  ░       ░ ░  
# VARS
define VENV_ERROR_MSG

   (╯°□°)╯︵ ┻━┻

   Dear developer, you need to activate venv first (Python >=3.12,<3.13).
   If you don't have venv, you can setup it by command → `python3 -m venv venv`
   Then run command → `source venv/bin/activate`

   ┬─┬ノ(°-°ノ)

endef
export VENV_ERROR_MSG

# Aiko
aiko.init:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$$VENV_ERROR_MSG"; \
		exit 1; \
	fi
	pip install poetry==2.1.3
	cd linter && poetry install --no-root

aiko.run:
	python3 -m core.app

# Tests
test:
	poetry run pytest

# Linter
lint.init:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$$VENV_ERROR_MSG"; \
		exit 1; \
	fi
	cd linter && poetry install --no-root

lint:
	cd linter && poetry run ruff format --config pyproject.toml ../core/
	cd linter && poetry run ruff check --config pyproject.toml --fix ../core/

lint.check:
	cd linter && poetry run ruff format --config pyproject.toml --check ../core/
	cd linter && poetry run ruff check --config pyproject.toml ../core/