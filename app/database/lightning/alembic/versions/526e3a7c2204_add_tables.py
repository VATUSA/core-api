"""Add Tables

Revision ID: 526e3a7c2204
Revises: 18bbb7b79b60
Create Date: 2023-05-19 16:02:46.394671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '526e3a7c2204'
down_revision = '18bbb7b79b60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('academy_course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('facility', sa.String(length=4), nullable=False),
    sa.Column('mdl_course_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=240), nullable=False),
    sa.Column('display_grade_on_profile', sa.Boolean(), nullable=True),
    sa.Column('allow_self_enroll', sa.Boolean(), nullable=True),
    sa.Column('is_auto_enroll', sa.Boolean(), nullable=True),
    sa.Column('allow_mentor_enroll', sa.Boolean(), nullable=True),
    sa.Column('mentor_enroll_required_rating', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('core_api_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('token', sa.String(length=80), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('can_read_all', sa.Boolean(), nullable=False),
    sa.Column('can_write_all', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transfer_hold',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('controller', sa.Integer(), nullable=False),
    sa.Column('hold', sa.String(length=120), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('is_released', sa.Boolean(), nullable=True),
    sa.Column('released_by_cid', sa.Integer(), nullable=True),
    sa.Column('created_by_cid', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_course_enrollment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course', sa.Integer(), nullable=True),
    sa.Column('controller', sa.Integer(), nullable=False),
    sa.Column('enrolled_by', sa.Integer(), nullable=False),
    sa.Column('enrolled_date', sa.DateTime(), nullable=False),
    sa.Column('is_expired', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['course'], ['academy_course.id'], name='fk_academy_course_enrollment_academy_course_id_course'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_exam',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course', sa.Integer(), nullable=True),
    sa.Column('facility', sa.String(length=4), nullable=False),
    sa.Column('mdl_quiz_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=240), nullable=False),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['course'], ['academy_course.id'], name='fk_academy_exam_academy_course_id_course'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('core_api_token_permission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('api_token', sa.Integer(), nullable=True),
    sa.Column('object', sa.String(length=120), nullable=False),
    sa.Column('can_read', sa.Boolean(), nullable=False),
    sa.Column('can_write', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['api_token'], ['core_api_token.id'], name='fk_core_api_token_permission_core_api_token_id_api_token'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_exam_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('academy_exam', sa.Integer(), nullable=True),
    sa.Column('controller', sa.Integer(), nullable=False),
    sa.Column('exam_date', sa.DateTime(), nullable=False),
    sa.Column('grade_percent', sa.Float(), nullable=False),
    sa.Column('require_retake', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['academy_exam'], ['academy_exam.id'], name='fk_academy_exam_result_academy_exam_id_academy_exam'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('academy_exam_result')
    op.drop_table('core_api_token_permission')
    op.drop_table('academy_exam')
    op.drop_table('academy_course_enrollment')
    op.drop_table('transfer_hold')
    op.drop_table('core_api_token')
    op.drop_table('academy_course')
    # ### end Alembic commands ###