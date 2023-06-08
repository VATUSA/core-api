from __future__ import annotations
import datetime
from typing import List, Optional, Set
import ormar
from app import constants
from .base import BaseMeta
from vatusa_core import models


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
    discord_id: Optional[str] = ormar.String(max_length=255, nullable=True)

    # Deprecated Fields
    access_token: str = ormar.Text(nullable=True)
    refresh_token: str = ormar.Text(nullable=True)
    token_expires: str = ormar.Text(nullable=True)
    cert_update: bool = ormar.Boolean(default=False)
    remember_token: str = ormar.String(max_length=255, nullable=True)
    prefname: bool = ormar.Boolean()
    prefname_date: datetime.datetime = ormar.DateTime(nullable=True)

    # Transitional Fields - Will be deprecated after conversion to lightning
    last_promotion: datetime.datetime = ormar.DateTime(nullable=True)
    flag_promotion_eligible: bool = ormar.Boolean(default=False)
    flag_transfer_eligible: bool = ormar.Boolean(default=False)
    flag_visit_eligible: bool = ormar.Boolean(default=False)
    flag_controller_interest: bool = ormar.Boolean(default=False)

    @staticmethod
    def query():
        return Controller.objects.prefetch_related([Controller.visits, Controller.roles, Controller.transfers])

    @classmethod
    async def get_by_cid(cls, cid: int) -> Controller:
        return await cls.query().filter(cid=cid).get_or_none()

    def to_response_model(self):
        return models.Controller(
            cid=self.cid,
            display_name=f'{self.fname} {self.lname}',
            first_name=self.fname,
            last_name=self.lname,
            email=self.email,
            facility=self.facility,
            rating=self.rating,
            rating_short=constants.rating.short_map.get(self.rating, 'UNK'),
            rating_long=constants.rating.long_map.get(self.rating, 'Unknown'),
            discord_id=self.discord_id,
            in_division=self.flag_homecontroller,
            receive_broadcast_emails=self.flag_broadcastOptedIn,
            prevent_staff_assignment=self.flag_preventStaffAssign,
            is_promotion_eligible=self.flag_promotion_eligible,
            is_transfer_eligible=self.flag_transfer_eligible,
            is_visit_eligible=self.flag_visit_eligible,
            is_controller_interest=self.flag_controller_interest,
            roles=[role.to_response_model() for role in self.roles],
            visits=[visit.facility for visit in self.visits],
        )

    async def update_restriction_flags(self):
        await self.load_all()

        # flag_promotion_eligible
        self.flag_promotion_eligible = (
            False if self.flag_homecontroller is False
            else False if self.rating < constants.rating.OBS
            else False if self.rating >= constants.rating.C1
            else False if True in [hold.hold in constants.hold.promotion_holds for hold in self.holds]
            else True
        )

        # flag_transfer_eligible
        self.flag_transfer_eligible = (
            False if self.flag_homecontroller is False
            else False if self.rating < constants.rating.OBS
            else False if self.rating in [constants.rating.I1, constants.rating.I2, constants.rating.I3]
            else False if True in [role.role in constants.hold.prevent_transfer_roles for role in self.roles]
            else False if True in [hold.hold in constants.hold.transfer_holds for hold in self.holds]
            else True
        )

        # flag_visit_eligible
        self.flag_visit_eligible = (
            False if self.rating < constants.rating.S1
            else False if self.facility == 'ZAE'
            else False if True in [hold.hold in constants.hold.visit_holds for hold in self.holds]
            else True
        )

        await self.update()

    def has_facility_role(self, facility: str, role: str) -> bool:
        return role in [r.role for r in self.roles if r.facility == facility]

    def is_facility_staff(self, facility: str) -> bool:
        return True in [self.has_facility_role(facility, role) for role in constants.roles.facility_staff_roles]


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

    def to_response_model(self):
        return models.ControllerRole(
            role=self.role,
            facility=self.facility
        )


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
    movements: Optional[int] = ormar.Integer(nullable=True)
    score: Optional[int] = ormar.Integer(nullable=True)
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

    @classmethod
    def query(cls):
        return cls.objects.prefetch_related([Transfer.cid])

    def to_response_model(self):
        return models.Transfer(
            id=self.id,
            controller=self.cid.to_response_model(),
            to_facility=self.to,
            from_facility=self.from_,
            reason=self.reason,
            created_at=self.created_at,
            approved=True if self.status == 1 else False if self.status == 2 else None,
            approved_by=self.actionby,
            approved_reason=self.actiontext,
            approved_at=self.updated_at
        )


class Visit(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'visits'

    id: int = ormar.Integer(primary_key=True)
    cid: Controller = ormar.ForeignKey(Controller)
    facility: str = ormar.String(max_length=3)
    created_at: datetime.datetime = ormar.DateTime()
    updated_at: datetime.datetime = ormar.DateTime()


class TransferHold(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'transfer_hold'
    id: int = ormar.Integer(primary_key=True)
    controller: Controller = ormar.ForeignKey(Controller, related_name='holds')
    hold: str = ormar.String(max_length=120)
    start_date: Optional[datetime.datetime] = ormar.DateTime(nullable=True)
    end_date: Optional[datetime.datetime] = ormar.DateTime(nullable=True)
    is_released: bool = ormar.Boolean(default=False)
    released_by_cid: Optional[int] = ormar.Integer(nullable=True, default=None)
    created_by_cid: Optional[int] = ormar.Integer(nullable=True)

    @staticmethod
    async def active_by_cid(cid: int) -> list[TransferHold]:
        holds: list[TransferHold] = await TransferHold.objects\
            .select_related(TransferHold.controller)\
            .filter(controller=cid)\
            .filter(is_released=False)\
            .filter((
                ((TransferHold.start_date.isnull(True)) | (TransferHold.start_date <= datetime.datetime.now()))
                & ((TransferHold.end_date.isnull(True)) | (TransferHold.end_date > datetime.datetime.now()))
            )).all()
        return holds

    def to_response_model(self):
        return models.TransferHold(
            id=self.id,
            controller=self.controller.to_response_model(),
            hold=self.hold,
            start_date=self.start_date,
            end_date=self.end_date,
            is_released=self.is_released,
            released_by_cid=self.released_by_cid,
            created_by_cid=self.created_by_cid,
        )
