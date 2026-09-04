from rest_framework.routers import DefaultRouter
from .views import HRReviewViewSet, LeaveApprovalViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("requests", LeaveRequestViewSet, basename="leave-request")
router.register("approvals", LeaveApprovalViewSet, basename="leave-approval")
router.register("hr-reviews", HRReviewViewSet, basename="hr-review")

urlpatterns = router.urls