UV ?= uv
PYTHON ?= python3

.PHONY: check-uv install install-prompting test-se run-project

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || (echo "uv no esta instalado. Instala uv y vuelve a ejecutar."; exit 1)

install: check-uv
	$(UV) sync

install-prompting: check-uv
	$(UV) sync

test-se: check-uv
	$(UV) run pytest -q

run-project: check-uv
	$(UV) run python src/multitasking_text_utility/run_query.py


