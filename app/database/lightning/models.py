from __future__ import annotations
import datetime

import ormar
from .base import BaseMeta


class AcademyCourse(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'academy_course'
    id: int = ormar.Integer(primary_key=True)
    facility: str = ormar.String(max_length=4)
    mdl_course_id: int = ormar.Integer()
    name: str = ormar.String(max_length=240)
    display_grade_on_profile: bool = ormar.Boolean(default=False)
    allow_self_enroll: bool = ormar.Boolean(default=False)
    is_auto_enroll: bool = ormar.Boolean(default=False)
    # is_auto_enroll is used to hide the 'Enroll' button for courses that use a moodle method (like cohort) to enroll
    allow_mentor_enroll: bool = ormar.Boolean(default=False)
    mentor_enroll_required_rating: int = ormar.Integer(nullable=True, default=None)


class AcademyCourseEnrollment(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'academy_course_enrollment'
    id: int = ormar.Integer(primary_key=True)
    course: AcademyCourse = ormar.ForeignKey(AcademyCourse)
    controller: int = ormar.Integer()
    enrolled_by: int = ormar.Integer()
    enrolled_date: datetime.datetime = ormar.DateTime()
    is_expired: bool = ormar.Boolean(default=False)


class AcademyExam(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'academy_exam'
    id: int = ormar.Integer(primary_key=True)
    course: AcademyCourse = ormar.ForeignKey(AcademyCourse)
    facility: str = ormar.String(max_length=4)
    mdl_quiz_id: int = ormar.Integer()
    name: str = ormar.String(max_length=240)
    is_enabled: bool = ormar.Boolean()


class AcademyExamResult(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'academy_exam_result'
    id = ormar.Integer(primary_key=True)
    academy_exam: AcademyExam = ormar.ForeignKey(AcademyExam)
    controller: int = ormar.Integer()
    exam_date: datetime.datetime = ormar.DateTime()
    grade_percent: float = ormar.Float()
    require_retake: bool = ormar.Boolean(default=False)


class APIRequestLog(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'api_log_request'
    request_id: str = ormar.String(max_length=120, primary_key=True)
    request_method: str = ormar.String(max_length=40)
    request_path: str = ormar.String(max_length=240)
    request_query_params: str = ormar.Text()
    api_key: str = ormar.String(max_length=120, nullable=True)
    user_cid: int = ormar.Integer(nullable=True)
    status_code: int = ormar.Integer()
    request_date: datetime.datetime = ormar.DateTime()


class APIErrorLog(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'api_log_error'
    error_id: str = ormar.String(max_length=120, primary_key=True)
    request_id: str = ormar.String(max_length=120)
    error_message: str = ormar.Text()
    error_traceback: str = ormar.Text(nullable=True)


class CoreAPIToken(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'core_api_token'
    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=120)
    token: str = ormar.String(max_length=80)
    enabled: bool = ormar.Boolean()
    can_read_all: bool = ormar.Boolean()
    can_write_all: bool = ormar.Boolean()


class CoreAPITokenPermission(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'core_api_token_permission'
    id: int = ormar.Integer(primary_key=True)
    api_token: CoreAPIToken = ormar.ForeignKey(CoreAPIToken, related_name='permissions')
    object: str = ormar.String(max_length=120)
    can_read: bool = ormar.Boolean()
    can_write: bool = ormar.Boolean()


class Session(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'session'
    session_id: str = ormar.String(max_length=120, primary_key=True)
    cid: int = ormar.Integer()
    issued_at: datetime.datetime = ormar.DateTime()
    expires: datetime.datetime = ormar.DateTime()
    is_invalidated: bool = ormar.Boolean(default=False)
    is_blocked: bool = ormar.Boolean(default=False)


class ManagedWorkspaceAccount(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'managed_workspace_account'
    id: int = ormar.Integer(primary_key=True)
    cid: int = ormar.Integer()
    username: str = ormar.String(max_length=80, nullable=True)
    can_self_serve: bool = ormar.Boolean(default=True)
    workspace_account_id: int = ormar.Integer(nullable=True, default=None)
    is_account_enabled: bool = ormar.Boolean(default=False)

    @classmethod
    def query(cls):
        return cls.objects.prefetch_related([ManagedWorkspaceAccount.aliases, ManagedWorkspaceAccount.aliases.domain])


class ManagedWorkspaceDomain(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'managed_workspace_domain'
    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=120)
    facility: str = ormar.String(max_length=4, nullable=True)
    is_enabled: bool = ormar.Boolean(default=False)

    @classmethod
    async def all_by_facility(cls, facility: str):
        return await cls.objects.filter(facility=facility).filter(is_enabled=True).all()


class ManagedWorkspaceAccountAlias(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'managed_workspace_account_domain'
    id: int = ormar.Integer(primary_key=True)
    account: ManagedWorkspaceAccount = ormar.ForeignKey(ManagedWorkspaceAccount, related_name='aliases')
    domain: ManagedWorkspaceDomain = ormar.ForeignKey(ManagedWorkspaceDomain)
    alias: str = ormar.String(max_length=80)

