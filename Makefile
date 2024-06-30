fmt:
	isort .
	black .
test:
	poetry run pytest .
style:
	pylint --fail-under=8 ./pysqltools/src/*

verify: style test