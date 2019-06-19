def UpdatePersonFromForm(person, form):
    # Update person and if selected - relatives

    person.name = form.cleaned_data["name"]
    person.email = form.cleaned_data["email"]
    person.phone = form.cleaned_data["phone"]
    person.birthday = form.cleaned_data["birthday"]
    person.city = form.cleaned_data["city"]
    person.zipcode = form.cleaned_data["zipcode"]
    person.streetname = form.cleaned_data["streetname"]
    person.housenumber = form.cleaned_data["housenumber"]
    person.floor = form.cleaned_data["floor"]
    person.door = form.cleaned_data["door"]
    person.placename = form.cleaned_data["placename"]
    person.dawa_id = form.cleaned_data["dawa_id"]
    person.save()

    if form.cleaned_data["address_global"] in "True":
        relatives = person.family.person_set.all()

        for relative in relatives:
            relative.city = form.cleaned_data["city"]
            relative.zipcode = form.cleaned_data["zipcode"]
            relative.streetname = form.cleaned_data["streetname"]
            relative.housenumber = form.cleaned_data["housenumber"]
            relative.floor = form.cleaned_data["floor"]
            relative.door = form.cleaned_data["door"]
            relative.placename = form.cleaned_data["placename"]
            relative.dawa_id = form.cleaned_data["dawa_id"]

            relative.save()
