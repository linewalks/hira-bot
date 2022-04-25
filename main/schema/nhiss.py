from marshmallow import fields, Schema, validate

from main.common.common import region_list


# schema
class ReservationNhissOnTime(Schema):
  name = fields.Str(required=True)
  id = fields.Str(required=True)
  password = fields.Str(required=True)
  is_seoul = fields.Bool(required=True)
  research_number = fields.Int(required=True)
  region = fields.Str(
      validate=validate.OneOf(region_list),
      required=True
  )
  research_visiter_list = fields.List(
      fields.Str(),
      required=True
  )


class ReservationNhissUntilSuccess(ReservationNhissOnTime):
  target_day = fields.Str(required=True)


class ReservationNhissCancel(Schema):
  task_id = fields.Str(required=True)
