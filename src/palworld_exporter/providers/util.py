def hex_uid_to_decimal(hex_str: str) -> str:
    """
    Palworld identifies players/saves with a 32-char hex UID
    (e.g. "13734CAA000000000000000000000000"). Only the first 8 hex
    characters vary; that prefix decoded as decimal is the player_uid
    used to join live player data with save file metadata.
    """
    return str(int(hex_str[:8], 16))
