"""Re-export всех моделей для Alembic autogenerate."""

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin  # noqa: F401
from app.models.user import FavoritePartner, OTPCode, User, UserRole, UserSession  # noqa: F401
from app.models.vehicle import CarBrand, CarModel, Vehicle  # noqa: F401
from app.models.partner import Partner, PartnerDocument, PartnerStatus, PartnerType, WorkSchedule  # noqa: F401
from app.models.catalog import (  # noqa: F401
    PartnerProduct,
    PartnerService,
    ProductCategory,
    ServiceCategory,
)
from app.models.booking import Booking, BookingStatus, Slot, SlotStatus  # noqa: F401
from app.models.order import Order, OrderItem, OrderStatus, OrderStatusHistory, OrderType  # noqa: F401
from app.models.payment import Payment, Payout, PayoutStatus, PromoCode  # noqa: F401
from app.models.notification import Notification, NotificationChannel, NotificationStatus  # noqa: F401
from app.models.emergency import (  # noqa: F401
    EmergencyRequest,
    EmergencyResponse,
    EmergencyStatus,
    EmergencyType,
    PartnerLocation,
)
from app.models.chat import (  # noqa: F401
    ChatMessage,
    ChatParticipant,
    ChatRoom,
    ChatRoomType,
    MessageStatus,
    MessageType,
)
from app.models.review import Review, ReviewFlag, ReviewHelpful, ReviewStatus  # noqa: F401
from app.models.content import Article, ContentType  # noqa: F401

__all__ = [
    "Base", "UUIDMixin", "TimestampMixin", "SoftDeleteMixin",
    "User", "UserRole", "UserSession", "OTPCode", "FavoritePartner",
    "CarBrand", "CarModel", "Vehicle",
    "Partner", "PartnerStatus", "PartnerType", "WorkSchedule", "PartnerDocument",
    "ServiceCategory", "PartnerService", "ProductCategory", "PartnerProduct",
    "Slot", "SlotStatus", "Booking", "BookingStatus",
    "Order", "OrderType", "OrderStatus", "OrderItem", "OrderStatusHistory",
    "Payment", "Payout", "PayoutStatus", "PromoCode",
    "Notification", "NotificationChannel", "NotificationStatus",
    # Phase 2
    "EmergencyRequest", "EmergencyResponse", "EmergencyStatus", "EmergencyType", "PartnerLocation",
    "ChatRoom", "ChatParticipant", "ChatMessage", "ChatRoomType", "MessageStatus", "MessageType",
    "Review", "ReviewFlag", "ReviewHelpful", "ReviewStatus",
    "Article", "ContentType",
]
