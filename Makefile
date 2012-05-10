clean:
	@find -name '*.py?' -or -name '.*.sw?' | xargs rm -f

test:
	@python test.py

lint:
	@pylint -E frames.py

watch:
	@guard start -c

release:
	@python setup.py register
