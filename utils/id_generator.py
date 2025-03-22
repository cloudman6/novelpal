import hashlib

class IDGenerator:
    @staticmethod
    def get_id(name):
        """生成确定性的哈希值"""
        hash_object = hashlib.sha256(name.encode())
        return hash_object.hexdigest()
