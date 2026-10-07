Finalement, tu pourrais demander à un ou deux utilisateurs s’ils reçoivent bien les notifications par mail dans Flowr PROD ? Merci !

python - <<'PY'
from alembic import command
from alembic.config import Config

cfg = Config("migrations/alembic.ini")
cfg.set_main_option("script_location", "migrations")
cfg.set_main_option("revision_environment", "false")

command.revision(
    cfg,
    message="add task assessor assigned email template",
    autogenerate=False,
)
PY