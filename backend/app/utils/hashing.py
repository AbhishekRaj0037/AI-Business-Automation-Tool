import hashlib

def checksum_from_part(part, algo="sha256", chunk_size=8192):
    hasher = hashlib.new(algo)

    payload = part.get_payload(decode=True)
    if payload is None:
        return None

    for i in range(0, len(payload), chunk_size):
        hasher.update(payload[i:i + chunk_size])

    return hasher.hexdigest()
