from enum import Enum


class UserRole(str, Enum):
    SALES = "SALES"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


class ClientType(str, Enum):
    COMPANY = "COMPANY"
    INDIVIDUAL = "INDIVIDUAL"


class ItemType(str, Enum):
    GARMENT = "GARMENT"
    SERVICE = "SERVICE"


class RateType(str, Enum):
    CONFECCION = "CONFECCION"


class QuoteStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    IN_PRODUCTION = "IN_PRODUCTION"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class OrderLineStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PRODUCTION = "IN_PRODUCTION"
    DONE = "DONE"


class ServiceStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    OUTSOURCED = "OUTSOURCED"


class ProductionStatus(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    VALIDATED = "VALIDATED"


class PayrollStatus(str, Enum):
    PRELIMINARY = "PRELIMINARY"
    APPROVED = "APPROVED"
    PAID = "PAID"


class ChangeRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
