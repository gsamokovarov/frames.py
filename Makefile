clean:
	@find -name '*.py?' -or -name '.*.sw?' | xargs rm -f

test:
	@tox

lint:
	@pylint -E frames.py

watch:
	@guard start -c

release:
	@python setup.py register

contributors:
	@python scripts/contributors.py > CONTRIBUTORS
