from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

from utils.helper import send_message
from nhiss.tasks.reservation_mode import start_delay
from main.common.common import region_dict, get_research_number_xpath
from main.schema.nhiss import ReservationNhiss


API_CATEGORY = "Nhiss"
nhiss_bp = Blueprint("nhiss", __name__, url_prefix="/api/nhiss")


@nhiss_bp.route("/reservation", methods=["GET"])
@use_kwargs(ReservationNhiss, location="query")
@doc(
    tags=[API_CATEGORY],
    summary="Nhiss 예약",
    description="Nhiss 예약햡니다."
)
def make_reservation_nhiss(name, id, password, is_seoul, research_number, target_day, region, research_visiter_list):
  
  research_number_xpath = get_research_number_xpath(research_number)

  region = "서울" if is_seoul else region
  research_center_xpath = region_dict.get(region)
  
  send_message(f"[Bot] {name}님 {region} 지역 공단봇 run_until_success 모드로 시작합니다. target day: {target_day}")
  start_delay(
      info=["안현정", "2022-04-29", "부산", False],
      headless=True,
      options={
          "name": name,
          "id": id,
          "password": password,
          "research_number_xpath": research_number_xpath,
          "research_center_xpath": research_center_xpath,
          "research_visiter_list": research_visiter_list
      }
  )
  return 200
