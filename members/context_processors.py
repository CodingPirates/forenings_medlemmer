def slack_menu_context(request):
    show_slack_menu = False
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.has_perm(
            "members.can_approve_slack_invites"
        ):
            show_slack_menu = True
    return {"show_slack_menu": show_slack_menu}
