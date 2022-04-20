from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

API_CATEGORY = "Nhiss"
nhiss_bp = Blueprint("nhiss", __name__, url_prefix="/api/nhiss")


@nhiss_bp.route("/reservation", methods=["GET"])
@doc(
    tags=[API_CATEGORY],
    summary="Nhiss 예약",
    description="Nhiss 예약햡내댜ㅣ"
)
def make_reservation_nhiss():
  return 200
