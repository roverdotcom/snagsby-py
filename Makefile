PYTHON_VERSION := 3.5


.PHONY: test
test: clean
	pytest -v -s


.PHONY: clean
clean:
	rm -rf .pytest*
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "*.pyc" -exec rm -f {} \;



.PHONY: docker-test
docker-test: clean
	docker run --rm \
		-v $(PWD):/app \
		-w /app \
		python:$(PYTHON_VERSION) \
		bash -c "pip install -r requirements-dev.txt && make"


.PHONY: docker-dist
docker-dist: clean
	docker run --rm \
		-v $(PWD):/app \
		-w /app \
		python:$(PYTHON_VERSION) \
		python setup.py sdist


# Watch python files and run tests
# https://github.com/joeyespo/pytest-watch
.PHONY: watch
watch:
	ptw --runner "make"
