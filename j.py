The utils submodule shows a - before its commit hash, meaning it hasn’t been initialized. That explains the missing shared code.

From flowr-mailer-api, run:

git submodule update --init --recursive

Once it finishes successfully, run:

export PYTHONPATH="$PWD/src:$PWD/utils/src${PYTHONPATH:+:$PYTHONPATH}"
python -m flask --app src/manage.py db revision \
  -m "add task assessor assigned email template"

This should create an empty migration file; it won’t insert the template yet. If either command fails, send me the new error.