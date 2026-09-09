def upgrade():
    op.execute(
        "ALTER TYPE userroleenum ADD VALUE IF NOT EXISTS 'SUPER_ADMIN'"
    )