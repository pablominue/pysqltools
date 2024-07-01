fmt:
	isort .
	black .
test:
	poetry run pytest -vv .
style:
	pylint --fail-under=8 ./pysqltools/src/*

verify: style test