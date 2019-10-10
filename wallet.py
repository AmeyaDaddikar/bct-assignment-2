
class Wallet:
  
  def __init__(self, secKey, pubKey, pwd):
    self.secKey = secKey
    self.pubKey = pubKey
    self.pwd    = pwd
    pass

  @staticmethod
  def generate(pwd):
    pass