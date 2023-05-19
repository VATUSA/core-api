from __future__ import annotations
import datetime
from typing import List, Optional, Set
import ormar

from .base import BaseMeta


class ActionLog(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'action_log'
    id: int = ormar.Integer(primary_key=True)
    from_: int = ormar.Integer(name='from')
    to: int = ormar.Integer()
    log: str = ormar.Text()
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()


class Controller(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'controllers'
    cid: int = ormar.Integer(primary_key=True)
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)
    email: str = ormar.String(max_length=255)
    facility: str = ormar.String(max_length=4)
    rating: int = ormar.Integer()
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()
    flag_needbasic: bool = ormar.Boolean(default=False)
    flag_xferOverride: bool = ormar.Boolean(default=False)
    facility_join: datetime.datetime = ormar.DateTime()
    flag_homecontroller: bool = ormar.Boolean()
    lastactivity: datetime.datetime = ormar.DateTime()
    flag_broadcastOptedIn: bool = ormar.Boolean(default=False)
    flag_preventStaffAssign: bool = ormar.Boolean(default=False)
    discord_id: str = ormar.String(max_length=255, nullable=True)
    last_promotion: datetime.datetime = ormar.DateTime(nullable=True)

    # Deprecated Fields
    access_token: str = ormar.Text(nullable=True)
    refresh_token: str = ormar.Text(nullable=True)
    token_expires: str = ormar.Text(nullable=True)
    cert_update: bool = ormar.Boolean(default=False)
    remember_token: str = ormar.String(max_length=255, nullable=True)
    prefname: bool = ormar.Boolean()
    prefname_date: datetime.datetime = ormar.DateTime(nullable=True)


class Facility(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'facilities'
    id: str = ormar.String(max_length=3, primary_key=True)
    name: str = ormar.String(max_length=255)
    url: str = ormar.String(max_length=255)
    hosted_email_domain: str = ormar.String(max_length=255, nullable=True)
    region: int = ormar.Integer()
    atm: int = ormar.Integer()
    datm: int = ormar.Integer()
    ta: int = ormar.Integer()
    ec: int = ormar.Integer()
    fe: int = ormar.Integer()
    wm: int = ormar.Integer()
    active: bool = ormar.Boolean()
    apikey: str = ormar.String(max_length=25)
    api_sandbox_key: str = ormar.String(max_length=255)
    welcome_text: str = ormar.Text()
    ace: bool = ormar.Boolean()
    url_dev: str = ormar.String(max_length=255)

    # Deprecated fields - should not be needed
    uls_return: str = ormar.String(max_length=255)
    uls_devreturn: str = ormar.String(max_length=255)
    uls_secret: str = ormar.String(max_length=255)
    uls_jwk: str = ormar.Text(nullable=True)
    apiv2_jwk: str = ormar.Text(nullable=True)
    apiv2_jwk_dev: str = ormar.String(max_length=255, nullable=True)
    ip: str = ormar.String(max_length=128)
    api_sandbox_ip: str = ormar.String(max_length=128)


class Promotion(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'promotions'
    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    grantor: int = ormar.Integer()
    to: int = ormar.Integer()
    from_: int = ormar.Integer(name='from')
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()
    exam: datetime.date = ormar.Date(nullable=True)
    examiner: int = ormar.Integer()
    position: str = ormar.String(max_length=11)
    eval_id: int = ormar.Integer(nullable=True)


class Role(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'roles'
    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    facility: str = ormar.String(max_length=3)
    role: str = ormar.String(max_length=12)
    created_at: datetime.datetime = ormar.DateTime()


class Solo(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'solo_certs'
    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    position: str = ormar.String(max_length=11)
    expires: datetime.date = ormar.Date(nullable=True)
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()


class TrainingRecord(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'training_records'
    id: int = ormar.Integer(primary_key=True)
    student_id: Controller = ormar.ForeignKey(Controller, related_name='tr_student')
    instructor_id: Controller = ormar.ForeignKey(Controller, related_name='tr_instructor')
    session_date: datetime.datetime = ormar.DateTime()
    facility_id: str = ormar.String(max_length=255)
    position: str = ormar.String(max_length=255)
    duration: datetime.time = ormar.Time()
    movements: int = ormar.Integer()
    score: int = ormar.Integer()
    notes: str = ormar.Text()
    location: int = ormar.SmallInteger()
    ots_status: int = ormar.SmallInteger()
    ots_eval_id: int = ormar.Integer(nullable=True)
    is_cbt: bool = ormar.Boolean()
    solo_granted: bool = ormar.Boolean()
    modified_by: int = ormar.Integer(nullable=True)
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()


class Transfer(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'transfers'
    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    to: str = ormar.String(max_length=3)
    from_: str = ormar.String(max_length=3, name='from')
    reason: str = ormar.Text()
    status: int = ormar.Integer()
    actiontext: str = ormar.Text(nullable=True, default=None)
    actionby: int = ormar.Integer(nullable=True, default=None)
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()


class Visit(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'visits'
    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    facility: str = ormar.String(max_length=3)
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()
    
