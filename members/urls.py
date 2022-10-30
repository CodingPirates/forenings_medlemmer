from django.urls import path
from members.views import (
    AccountCreate,
    Activities,
    ActivitySignup,
    AdminSignup,
    ConfirmFamily,
    DeclineInvitation,
    DepartmentSignView,
    EntryPage,
    FamilyDetails,
    Membership,
    PersonCreate,
    PersonUpdate,
    QuickpayCallback,
    SupportMembership,
    WaitingListSetSubscription,
    departmentView,
    paymentGatewayErrorView,
    userCreated,
    volunteerSignup,
)
from django.contrib.auth import views as auth_views
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(r"^$", EntryPage, name="entry_page"),
    path(r"^graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path(r"^account/create/$", AccountCreate, name="account_create"),
    path(
        r"^account/login/$",
        auth_views.LoginView.as_view(template_name="members/login.html"),
        name="person_login",
    ),
    path(
        r"^account/forgot/$",
        auth_views.PasswordResetView.as_view(template_name="members/forgot.html"),
        {
            "email_template_name": "members/email/password_reset.txt",
            "html_email_template_name": "members/email/password_reset.html",
            "subject_template_name": "members/email/password_reset_subject.txt",
        },
        name="password_reset",
    ),
    path(
        r"^account/forgot/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="members/forgot_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        r"^account/forgot/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="members/forgot_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        r"^account/forgot/complete/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="members/forgot_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        r"^account/logout/$",
        auth_views.LogoutView.as_view(template_name="members/logout.html"),
        {"next_page": "/"},
        name="person_logout",
    ),
    path(r"^activities/$", Activities, name="activities"),
    path(r"^membership/$", Membership, name="membership"),
    path(r"^support_membership/$", SupportMembership, name="support_membership"),
    path(r"^volunteer$", volunteerSignup, name="volunteer_signup"),
    path(r"^user_created/$", userCreated, name="user_created"),
    path(r"^admin_signup/$", AdminSignup, name="admin_signup"),
    path(r"^family/$", FamilyDetails, name="family_detail"),
    path(r"^family/Person/(?P<id>[\d]+)/$", PersonUpdate, name="person_update"),
    path(r"^family/Person/(?P<membertype>[A-Z]{2})$", PersonCreate, name="person_add"),
    path(
        r"^family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/$",
        ActivitySignup,
        name="activity_signup",
    ),
    path(
        r"^family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/view/$",
        ActivitySignup,
        name="activity_view_person",
    ),
    path(
        r"^family/activity/(?P<activity_id>[\d]+)/view/$",
        ActivitySignup,
        name="activity_view_family",
    ),
    path(
        r"^family/(?P<unique>[\w-]+)/invitation_decline/(?P<invitation_id>[\d]+)/$",
        DeclineInvitation,
        name="invitation_decline",
    ),
    path(
        r"^family/payment_gateway_error$",
        paymentGatewayErrorView,
        name="payment_gateway_error_view",
    ),
    path(r"^confirm_details/$", ConfirmFamily, name="confirm_details"),
    path(
        r"^waiting_list/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/(?P<action>(subscribe|unsubscribe))/$",
        WaitingListSetSubscription,
        name="waiting_list_subscription",
    ),
    path(r"^activity/(?P<activity_id>[\d]+)/$", ActivitySignup, name="activity_view"),
    path(r"^quickpay_callback$", QuickpayCallback, name="quickpay_callback"),
    path(r"^department_signup$", DepartmentSignView, name="department_signup"),
    path(r"^departments$", departmentView, name="department_view"),
]
