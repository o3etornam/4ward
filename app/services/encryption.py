from Crypto.Cipher import AES
import binascii

from loguru import logger  # Import the logger from main

class AESProcessor:
    def __init__(self):
        # AES encryption logic would go here
        pass
    
    def encrypt(self, data, key):
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.encrypt(data)

class PaymentEncryption:
    CONST_AES_KEY_BYTES = 16
    
    def __init__(self, root_key):
        self.m_rootkey = binascii.unhexlify(root_key)
        
    def ascii_to_16_bytes(self, raw_str):
        if not raw_str:
            return None
            
        if len(raw_str) > self.CONST_AES_KEY_BYTES:
            raw_str = raw_str[:self.CONST_AES_KEY_BYTES]
            
        str_bytes = raw_str.encode('ascii')
        result_bytes = bytearray(self.CONST_AES_KEY_BYTES)
        result_bytes[:len(str_bytes)] = str_bytes
        
        return bytes(result_bytes)
    
    def bytes_to_ascii_string(self, bytes_data):
        return bytes_data.decode('ascii').rstrip('\x00')
    
    def bytes_to_hex_string(self, bytes_data):
        if not bytes_data:
            return ""
        return binascii.hexlify(bytes_data).decode('ascii').upper()
    
    def hex_string_to_bytes(self, hex_str):
        if not hex_str or len(hex_str) % 2 != 0:
            return None
        
        try:
            return binascii.unhexlify(hex_str)
        except binascii.Error:
            return None
    
    def generate_purchase_string(self, transaction_id, payment):
        """Generate purchase string from transaction ID and payment amount"""
        # Convert transaction ID to bytes
        transid_bytes = self.ascii_to_16_bytes(transaction_id)
        logger.debug(f"Transaction ID: {self.bytes_to_hex_string(transid_bytes)}")
        
        # Encrypt transaction ID using root key
        aes = AESProcessor()
        encrypted_transaction = aes.encrypt(transid_bytes, self.m_rootkey)
        logger.debug(f"Encrypted transaction ID: {self.bytes_to_hex_string(encrypted_transaction)}")
        
        # Convert payment to string with 2 decimal places
        payment_str = f"{payment:.2f}"
        payment_bytes = self.ascii_to_16_bytes(payment_str)
        logger.debug(f"Payment: {self.bytes_to_hex_string(payment_bytes)}")
        
        # Encrypt payment using encrypted transaction ID as key
        purchase_bytes = aes.encrypt(payment_bytes, encrypted_transaction)
        logger.debug(f"Encrypted purchase parameter: {self.bytes_to_hex_string(purchase_bytes)}")
        
        # Convert to hex string
        hex_str = self.bytes_to_hex_string(purchase_bytes)
        logger.debug(f"Purchase string: {hex_str}")
        
        return hex_str


if __name__ == "__main__":
  test = PaymentEncryption('DCC78B3DAC5CA7409A01F45D81106753')
  test.generate_purchase_string('ac3307bcca7445618071e6b0e41b50b5',10)
