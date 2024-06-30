fmt:
	isort .
	black .
test:
	poetry run pytest .
	poetry run coverage report
style:
	pylint ./pysqltools/src/*

verify: style test