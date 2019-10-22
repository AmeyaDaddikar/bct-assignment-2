from Crypto.PublicKey import ECC
import json

class Wallet:
  
  def __init__(self, wallet_name, secKey, passphrase):
    """
    __init__ Creates a Wallet object compliant to the Blockchain. 
    
    The Wallet can be used with any GUI for transacting with the blockchain
    NOTE:: This function should not be used publicaly. Instead use the method geterate() to create
    
    :param wallet_name: Name of the wallet
    :type wallet_name : string
    :param secKey     : A Private Key Instance having the capability to generate its PublicKey on demand
    :type secKey      : Crypto.PublicKey.ECC.EccKey
    :param passphrase : A password to protect the wallet when saved on disk
    :type passphrase  : string
    """
    self.secKey      = secKey
    self.passphrase  = passphrase
    self.wallet_name = wallet_name

  @property
  def pubKey(self):
    return self.secKey.public_key()

  @staticmethod
  def generate(wallet_name, passphrase):
    return Wallet(wallet_name, ECC.generate(curve='prime256v1'), passphrase)
  
  @staticmethod
  def restore(file_path, passphrase):
    with open(file_path, 'rt') as f:
      wallet_details = json.load(f)

      secKey = ECC.import_key(wallet_details['secKey'], passphrase=passphrase)

      return Wallet(wallet_details['wallet_name'], secKey, passphrase)



  def save(self, file_path=None):

    if file_path is None:
      file_path = f'private/{self.wallet_name}.json'

    wallet_details = {
      'secKey'     : self.secKey.export_key(format='PEM', passphrase=self.passphrase, protection='PBKDF2WithHMAC-SHA1AndAES128-CBC'),
      'pubKey'     : self.pubKey.export_key(format='PEM'),
      'wallet_name': self.wallet_name
    }

    with open(file_path, 'wt') as f:
      f.write(json.dumps(wallet_details, indent=0))



def test():
    wallet1 = Wallet.generate('walletx', 'password')
    wallet1.save()

    wallet2 = Wallet.restore(f'private/{wallet1.wallet_name}.json', wallet1.passphrase)

    print(wallet1.secKey.export_key(format='PEM') == wallet2.secKey.export_key(format='PEM'))

if __name__ == '__main__':
    test()
    