from django.core.management.base import BaseCommand
from members.models import Municipality

# Source: api.dataforsyningen.dk/kommuner — stable since the 2007 municipal reform
_MUNICIPALITY_REGIONS = {
    "0101": "Region Hovedstaden",
    "0147": "Region Hovedstaden",
    "0151": "Region Hovedstaden",
    "0153": "Region Hovedstaden",
    "0155": "Region Hovedstaden",
    "0157": "Region Hovedstaden",
    "0159": "Region Hovedstaden",
    "0161": "Region Hovedstaden",
    "0163": "Region Hovedstaden",
    "0165": "Region Hovedstaden",
    "0167": "Region Hovedstaden",
    "0169": "Region Hovedstaden",
    "0173": "Region Hovedstaden",
    "0175": "Region Hovedstaden",
    "0183": "Region Hovedstaden",
    "0185": "Region Hovedstaden",
    "0187": "Region Hovedstaden",
    "0190": "Region Hovedstaden",
    "0201": "Region Hovedstaden",
    "0210": "Region Hovedstaden",
    "0217": "Region Hovedstaden",
    "0219": "Region Hovedstaden",
    "0223": "Region Hovedstaden",
    "0230": "Region Hovedstaden",
    "0240": "Region Hovedstaden",
    "0250": "Region Hovedstaden",
    "0260": "Region Hovedstaden",
    "0270": "Region Hovedstaden",
    "0400": "Region Hovedstaden",
    "0411": "Region Hovedstaden",
    "0253": "Region Sjælland",
    "0259": "Region Sjælland",
    "0265": "Region Sjælland",
    "0269": "Region Sjælland",
    "0306": "Region Sjælland",
    "0316": "Region Sjælland",
    "0320": "Region Sjælland",
    "0326": "Region Sjælland",
    "0329": "Region Sjælland",
    "0330": "Region Sjælland",
    "0336": "Region Sjælland",
    "0340": "Region Sjælland",
    "0350": "Region Sjælland",
    "0360": "Region Sjælland",
    "0370": "Region Sjælland",
    "0376": "Region Sjælland",
    "0390": "Region Sjælland",
    "0410": "Region Syddanmark",
    "0420": "Region Syddanmark",
    "0430": "Region Syddanmark",
    "0440": "Region Syddanmark",
    "0450": "Region Syddanmark",
    "0461": "Region Syddanmark",
    "0479": "Region Syddanmark",
    "0480": "Region Syddanmark",
    "0482": "Region Syddanmark",
    "0492": "Region Syddanmark",
    "0510": "Region Syddanmark",
    "0530": "Region Syddanmark",
    "0540": "Region Syddanmark",
    "0550": "Region Syddanmark",
    "0561": "Region Syddanmark",
    "0563": "Region Syddanmark",
    "0573": "Region Syddanmark",
    "0575": "Region Syddanmark",
    "0580": "Region Syddanmark",
    "0607": "Region Syddanmark",
    "0621": "Region Syddanmark",
    "0630": "Region Syddanmark",
    "0615": "Region Midtjylland",
    "0657": "Region Midtjylland",
    "0661": "Region Midtjylland",
    "0665": "Region Midtjylland",
    "0671": "Region Midtjylland",
    "0706": "Region Midtjylland",
    "0707": "Region Midtjylland",
    "0710": "Region Midtjylland",
    "0727": "Region Midtjylland",
    "0730": "Region Midtjylland",
    "0740": "Region Midtjylland",
    "0741": "Region Midtjylland",
    "0746": "Region Midtjylland",
    "0751": "Region Midtjylland",
    "0756": "Region Midtjylland",
    "0760": "Region Midtjylland",
    "0766": "Region Midtjylland",
    "0779": "Region Midtjylland",
    "0791": "Region Midtjylland",
    "0773": "Region Nordjylland",
    "0787": "Region Nordjylland",
    "0810": "Region Nordjylland",
    "0813": "Region Nordjylland",
    "0820": "Region Nordjylland",
    "0825": "Region Nordjylland",
    "0840": "Region Nordjylland",
    "0846": "Region Nordjylland",
    "0849": "Region Nordjylland",
    "0851": "Region Nordjylland",
    "0860": "Region Nordjylland",
}


class Command(BaseCommand):
    help = "Populate the region field on all Municipality records"

    def handle(self, *args, **options):
        updated = 0
        skipped = 0

        for municipality in Municipality.objects.all():
            region = _MUNICIPALITY_REGIONS.get(municipality.dawa_id)
            if region:
                municipality.region = region
                municipality.save(update_fields=["region"])
                updated += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No region found for {municipality.name} (dawa_id={municipality.dawa_id})"
                    )
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} municipalities, skipped {skipped}")
        )
