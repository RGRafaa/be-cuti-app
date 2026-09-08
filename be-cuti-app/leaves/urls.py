from django.urls import path
from rest_framework.routers import DefaultRouter

from .balance import SaldoCutiView
from .dashboard import DashboardView
from .views import HRReviewViewSet, LeaveApprovalViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("requests", LeaveRequestViewSet, basename="leave-request")
router.register("approvals", LeaveApprovalViewSet, basename="leave-approval")
router.register("hr-reviews", HRReviewViewSet, basename="hr-review")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("saldo/", SaldoCutiView.as_view(), name="saldo-cuti"),
] + router.urls