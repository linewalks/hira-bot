class RegisterInfo:
  def __init__(self, user_name, target_day, region, is_register_am, is_seoul: bool = False):
    self.user_name = user_name
    self.target_day = target_day
    self.region = region
    self.is_register_am = is_register_am
    self.is_seoul = is_seoul

  def getInfo(self):
    return {
      'user_name': self.user_name,
      'target_day': self.target_day,
      'region': self.region,
      'is_register_am': self.is_register_am,
      'is_seoul': self.is_seoul
    }
