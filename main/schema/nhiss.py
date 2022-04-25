from marshmallow import fields, Schema, validate

from main.common.common import region_list


# schema
class ReservationNhissOnTime(Schema):
  name = fields.Str(
      required=True,
      description="예약 하는 사용자의 이름"
  )
  id = fields.Str(
      required=True,
      description="NHISS 로그인 아이디"
  )
  password = fields.Str(
      required=True,
      description="NHISS 로그인 패스워드"
  )
  is_seoul = fields.Bool(
      required=True,
      description="PC예약신청(서울) 유무"
  )
  research_number = fields.Int(
      required=True,
      description="연구과제관리번호 ex) 1 첫번째 위치의 연구과제"
  )
  region = fields.Str(
      validate=validate.OneOf(region_list),
      required=True,
      description="센터 지역"
  )
  research_visiter_list = fields.List(
      fields.Str(),
      required=True,
      description="방문자 등록"
  )


class ReservationNhissUntilSuccess(ReservationNhissOnTime):
  target_day = fields.Str(
      required=True,
      description="target_day: XXXX-XX-XX 형식으로 기입"
  )


class ReservationNhissCancel(Schema):
  task_id = fields.Str(required=True)
