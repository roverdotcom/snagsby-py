test: clean
	pytest -v -s
.PHONY: test

clean:
	rm -rf .pytest*
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "*.pyc" -exec rm -f {} \;
.PHONY: clean

docker-test: clean
	docker run --rm \
		-v $(PWD):/app \
		-w /app \
		python:2.7 \
		bash -c "pip install -r requirements-dev.txt && make"
	docker run --rm \
		-v $(PWD):/app \
		-w /app \
		python:3.5 \
		bash -c "pip install -r requirements-dev.txt && make"
.PHONY: docker-test

# Watch python files and run tests
# https://github.com/joeyespo/pytest-watch
watch:
	ptw --runner "make"
.PHONY: watch
