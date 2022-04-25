region_list = [
    "원주 본부",
    "명동",
    "명동(리서치)",
    "경인",
    "대전",
    "광주",
    "대구",
    "부산",
    "전주",
    "청주",
    "일산병원"
]

region_dict = {
    resion: f"/html/body/div[6]/div/table/tbody/tr[{idx + 1}]/td[2]"
    for idx, resion in enumerate(region_list)
}


def get_research_number_xpath(number):
  return f"/html/body/div[5]/div/table/tbody/tr[{number + 1}]/td[2]"
