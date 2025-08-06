env:
	@echo "* creating new environment"
	@if [ -z "$$VIRTUAL_ENV" ];\
	then\
		uv venv --seed --prompt simple-gmail-agent --python 3.11;\
		uv sync;\
		uv sync --dev;\
		uv pip install -e .;\
		echo "* enter virtual environment with all development dependencies now";\
		echo "* run 'source .venv/bin/activate' to enter the development environment.";\
	else\
		uv sync;\
		uv pip install -e .;\
		echo "* already in a virtual environment (exit first ('deactivate') to create a new environment)";\
	fi