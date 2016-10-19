.PHONY :test
test:
	nosetests -v -s

.PHONY :docker-test
docker-test:
	docker run --rm \
		-v $(PWD):/app:ro \
		-w /app \
		python:2.7 \
		bash -c "pip install -r requirements-dev.txt && make"

# Watch python files and run tests
# https://github.com/joeyespo/pytest-watch
.PHONY :watch
watch:
	ptw --runner "make"
