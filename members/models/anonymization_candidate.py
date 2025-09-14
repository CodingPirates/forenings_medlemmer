from .person import Person


class AnonymizationCandidate(Person):
    """
    Proxy model for Person to create a separate admin view for anonymization candidates.
    This allows us to have different admin behavior for the same underlying Person model.
    """

    class Meta:
        proxy = True
        verbose_name = "Anonymiserings kandidat"
        verbose_name_plural = "Anonymiserings kandidater"
