from datetime import datetime, timedelta
from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

from utils.helper import send_message, validate
from nhiss.tasks.reservation_mode import run_until_success, run_on_time
from background.nhiss import stop_celery_task
from main.common.common import region_dict, get_research_number_xpath, get_countdown
from main.schema.nhiss import (
    ReservationNhissOnTime,
    ReservationNhissUntilSuccess,
    ReservationNhissCancel
)


API_CATEGORY = "Nhiss"
nhiss_bp = Blueprint("nhiss", __name__, url_prefix="/api/nhiss")


@nhiss_bp.route("/reservation/until-success", methods=["GET"])
@use_kwargs(ReservationNhissUntilSuccess, location="query")
@doc(
    tags=[API_CATEGORY],
    summary="Nhiss until-success 예약",
    description="Nhiss until-success 모드로 예약햡니다."
)
def make_reservation_nhiss_until_success(name, id, password, is_seoul, research_number, target_day, region, research_visiter_list):
  if target_day:
    try:
      validate(target_day)
    except ValueError as e:
      send_message("옳바른 형식의 target_day를 넣어 주세요. ex)xxxx-xx-xx")
      return {"message": "옳바른 형식의 target_day를 넣어 주세요 ex)xxxx-xx-xx"}, 400

  research_number_xpath = get_research_number_xpath(research_number)

  region = "서울" if is_seoul else region
  research_center_xpath = region_dict.get(region)

  send_message(f"[Bot] {name}님 {region} 지역 공단봇 run_until_success 모드로 시작합니다. target day: {target_day}")

  run_until_success.delay(
      info=[name, target_day, region, False],
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
  return {"message": "예약 신청에 성공 하였습니다."}, 200


@nhiss_bp.route("/reservation/on-time", methods=["GET"])
@use_kwargs(ReservationNhissOnTime, location="query")
@doc(
    tags=[API_CATEGORY],
    summary="Nhiss on-time 예약",
    description="Nhiss on-time 모드로 예약햡니다."
)
def make_reservation_nhiss_on_time(name, id, password, is_seoul, research_number, region, research_visiter_list):
  target_day = (datetime.now() + timedelta(days = 15)).strftime("%Y-%m-%d")

  research_number_xpath = get_research_number_xpath(research_number)

  region = "서울" if is_seoul else region
  research_center_xpath = region_dict.get(region)
  
  send_message(f"[Bot] {name}님 {region} 지역 공단봇 run_on_time 모드로 시작합니다. target day: {target_day}")

  countdown = get_countdown()

  run_on_time.apply_async(
      kwargs={
          "info": [name, target_day, region, False],
          "headless": True,
          "debug": False,
          "options": {
              "name": name,
              "id": id,
              "password": password,
              "research_number_xpath": research_number_xpath,
              "research_center_xpath": research_center_xpath,
              "research_visiter_list": research_visiter_list
          }
      },
      countdown=countdown
  )
  return {"message": "예약 신청에 성공 하였습니다."}, 200


@nhiss_bp.route("/reservation/cancel", methods=["GET"])
@use_kwargs(ReservationNhissCancel, location="query")
@doc(
    tags=[API_CATEGORY],
    summary="Nhiss 예약 취소",
    description="Nhiss 예약을 취소햡니다."
)
def cancel_reservation_nhiss(task_id):
  task_id = task_id.strip()
  stop_celery_task(task_id)
  send_message(f"task_id: {task_id} 예약을 취소합니다.")
  return {"message": "예약 취소가 성공 하였습니다."}, 200
