from members.utils.address_lookup import get_address_by_id, parse_address_data


def get_user_region(person):
    if not person.dawa_id:
        return None
    try:
        data = get_address_by_id(person.dawa_id)
        if not data:
            return None
        return parse_address_data(data)["region"] or None
    except Exception:
        return None
