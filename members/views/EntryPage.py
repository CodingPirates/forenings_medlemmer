from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render


@xframe_options_exempt
def EntryPage(request):
    return render(request, "members/entry_page.html")
