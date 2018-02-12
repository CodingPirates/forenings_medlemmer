import hashlib
import hmac

def signQuickpay(base, private_key):
    return hmac.new(private_key, base, hashlib.sha256).hexdigest()
