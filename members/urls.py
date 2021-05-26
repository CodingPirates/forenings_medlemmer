from django.conf.urls import url
from members.views import (
    FamilyDetails,
    PersonCreate,
    PersonUpdate,
    WaitingListSetSubscription,
    DeclineInvitation,
    EntryPage,
    userCreated,
    ConfirmFamily,
    QuickpayCallback,
    ActivitySignup,
    DepartmentSignView,
    paymentGatewayErrorView,
    volunteerSignup,
    departmentView,
    Activities,
    Membership,
    SupportMembership,
    AdminSignup,
)
from django.contrib.auth import views as auth_views
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r"^$", EntryPage, name="entry_page"),
    url(r"^graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    url(
        r"^account/login/$",
        auth_views.LoginView.as_view(template_name="members/login.html"),
        name="person_login",
    ),
    url(
        r"^account/forgot/$",
        auth_views.PasswordResetView.as_view(template_name="members/forgot.html"),
        {
            "email_template_name": "members/email/password_reset.txt",
            "html_email_template_name": "members/email/password_reset.html",
            "subject_template_name": "members/email/password_reset_subject.txt",
        },
        name="password_reset",
    ),
    url(
        r"^account/forgot/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="members/forgot_done.html"
        ),
        name="password_reset_done",
    ),
    url(
        r"^account/forgot/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="members/forgot_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    url(
        r"^account/forgot/complete/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="members/forgot_complete.html"
        ),
        name="password_reset_complete",
    ),
    url(
        r"^account/logout/$",
        auth_views.LogoutView.as_view(template_name="members/logout.html"),
        {"next_page": "/"},
        name="person_logout",
    ),
    url(r"^activities/$", Activities, name="activities"),
    url(r"^membership/$", Membership, name="membership"),
    url(r"^support_membership/$", SupportMembership, name="support_membership"),
    url(r"^volunteer$", volunteerSignup, name="volunteer_signup"),
    url(r"^user_created/$", userCreated, name="user_created"),
    url(r"^admin_signup/$", AdminSignup, name="admin_signup"),
    url(r"^family/$", FamilyDetails, name="family_detail"),
    url(r"^family/Person/(?P<id>[\d]+)/$", PersonUpdate, name="person_update"),
    url(r"^family/Person/(?P<membertype>[A-Z]{2})$", PersonCreate, name="person_add"),
    url(
        r"^family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/$",
        ActivitySignup,
        name="activity_signup",
    ),
    url(
        r"^family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/view/$",
        ActivitySignup,
        name="activity_view_person",
    ),
    url(
        r"^family/activity/(?P<activity_id>[\d]+)/view/$",
        ActivitySignup,
        name="activity_view_family",
    ),
    url(
        r"^family/(?P<unique>[\w-]+)/invitation_decline/(?P<invitation_id>[\d]+)/$",
        DeclineInvitation,
        name="invitation_decline",
    ),
    url(
        r"^family/payment_gateway_error$",
        paymentGatewayErrorView,
        name="payment_gateway_error_view",
    ),
    url(r"^confirm_details/$", ConfirmFamily, name="confirm_details"),
    url(
        r"^waiting_list/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/(?P<action>(subscribe|unsubscribe))/$",
        WaitingListSetSubscription,
        name="waiting_list_subscription",
    ),
    url(r"^activity/(?P<activity_id>[\d]+)/$", ActivitySignup, name="activity_view"),
    url(r"^quickpay_callback$", QuickpayCallback, name="quickpay_callback"),
    url(r"^department_signup$", DepartmentSignView, name="department_signup"),
    url(r"^departments$", departmentView, name="department_view"),
]
