def UpdatePersonFromForm(person, personform, addressform):
    # Update person and if selected - relatives
    if person.membertype == "CH":
        person.name = personform.cleaned_data["child_name"]
        person.email = personform.cleaned_data["child_email"]
        person.phone = personform.cleaned_data["child_phone"]
        person.birthday = personform.cleaned_data["child_birthday"]
    else:
        person.name = personform.cleaned_data["parent_name"]
        person.email = personform.cleaned_data["parent_email"]
        person.phone = personform.cleaned_data["parent_phone"]
        person.birthday = personform.cleaned_data["parent_birthday"]

    person.city = addressform.cleaned_data["city"]
    person.zipcode = addressform.cleaned_data["zipcode"]
    person.streetname = addressform.cleaned_data["streetname"]
    person.housenumber = addressform.cleaned_data["housenumber"]
    person.floor = addressform.cleaned_data["floor"]
    person.door = addressform.cleaned_data["door"]
    person.placename = addressform.cleaned_data["placename"]
    person.dawa_id = addressform.cleaned_data["dawa_id"]
    person.save()

    if addressform.cleaned_data["update_family"] == "True":
        relatives = person.family.person_set.all()

        for relative in relatives:
            relative.city = addressform.cleaned_data["city"]
            relative.zipcode = addressform.cleaned_data["zipcode"]
            relative.streetname = addressform.cleaned_data["streetname"]
            relative.housenumber = addressform.cleaned_data["housenumber"]
            relative.floor = addressform.cleaned_data["floor"]
            relative.door = addressform.cleaned_data["door"]
            relative.placename = addressform.cleaned_data["placename"]
            relative.dawa_id = addressform.cleaned_data["dawa_id"]

            relative.save()
