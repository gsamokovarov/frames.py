clean:
	@find -name '*.py?' -or -name '.*.sw?' | xargs rm -f

test:
	@py.test -v test.py

lint:
	@pylint -E frames.py

watch:
	@guard start -c

release:
	@python setup.py register

contributors:
	@python scripts/contributors.py > CONTRIBUTORS
