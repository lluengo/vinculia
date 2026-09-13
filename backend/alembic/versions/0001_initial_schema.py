"""Initial schema: pacientes, actividades, sesiones_juego

Revision ID: 0001
Revises: 
Create Date: 2026-09-12 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear tabla pacientes
    op.create_table(
        'pacientes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id', ondelete='CASCADE'), nullable=True),
        sa.Column('apodo', sa.String(length=100), nullable=False),
        sa.Column('edad', sa.Integer(), nullable=True),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('eliminado_en', sa.DateTime(), nullable=True),
        sa.Column('ultima_sesion', sa.DateTime(), nullable=True),
        sa.CheckConstraint('edad > 0', name='pacientes_edad_check')
    )
    op.create_index(op.f('ix_pacientes_profesional_id'), 'pacientes', ['profesional_id'], unique=False)

    # 2. Crear tabla actividades
    op.create_table(
        'actividades',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id', ondelete='CASCADE'), nullable=True),
        sa.Column('paciente_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pacientes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tipo_plantilla', sa.String(length=50), nullable=False, server_default='asociacion'),
        sa.Column('titulo', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.String(length=500), nullable=True),
        sa.Column('modo', sa.String(length=50), nullable=False, server_default='imagen-imagen'),
        sa.Column('pares', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('configuracion', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('token_acceso', sa.String(length=100), nullable=True),
        sa.Column('expira_en', sa.DateTime(), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('eliminado_en', sa.DateTime(), nullable=True),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )
    op.create_index(op.f('ix_actividades_token_acceso'), 'actividades', ['token_acceso'], unique=True)
    op.create_index(op.f('ix_actividades_profesional_id'), 'actividades', ['profesional_id'], unique=False)
    op.create_index(op.f('ix_actividades_paciente_id'), 'actividades', ['paciente_id'], unique=False)

    # 3. Crear tabla sesiones_juego
    op.create_table(
        'sesiones_juego',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('paciente_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=True),
        sa.Column('actividad_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actividades.id', ondelete='CASCADE'), nullable=True),
        sa.Column('tiempo_segundos', sa.Integer(), nullable=False),
        sa.Column('aciertos', sa.Integer(), nullable=False),
        sa.Column('errores', sa.Integer(), nullable=False),
        sa.Column('completado_en', sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )
    op.create_index(op.f('ix_sesiones_juego_paciente_id'), 'sesiones_juego', ['paciente_id'], unique=False)
    op.create_index(op.f('ix_sesiones_juego_actividad_id'), 'sesiones_juego', ['actividad_id'], unique=False)


def downgrade() -> None:
    op.drop_table('sesiones_juego')
    op.drop_table('actividades')
    op.drop_table('pacientes')
