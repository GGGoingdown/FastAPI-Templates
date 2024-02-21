.PHONY: create
create:
	cookiecutter --no-input -f ./ -o ./test_template project_name="testing project"
