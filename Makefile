.PHONY: check validate build linkcheck lint-actions

# One-command entry point: all checks a contributor or reviewer needs.
check: validate build linkcheck lint-actions

validate:
	python3 scripts/validate_readme.py

build:
	python3 scripts/build_site.py

linkcheck:
	@command -v lychee >/dev/null 2>&1 || { echo "lychee not installed. Install it: brew install lychee (see https://github.com/lycheeverse/lychee)"; exit 1; }
	lychee --accept 200,201,202,203,204,206,301,302,303,307,308,403,429,999 --no-progress README.md

lint-actions:
	@command -v actionlint >/dev/null 2>&1 || { echo "actionlint not installed. Install it: brew install actionlint (see https://github.com/rhysd/actionlint)"; exit 1; }
	actionlint
