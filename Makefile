fmt:
	isort .
	black .
test:
	poetry run pytest .
	poetry run coverage report
style:
	pylint ./src/*

verify: style test