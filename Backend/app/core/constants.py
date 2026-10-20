class Role:
    WORKER = "worker"
    EMPLOYER = "employer"
    ADMIN = "admin"


class JobStatus:
    DRAFT = "draft"
    OPEN = "open"
    FILLED = "filled"
    CLOSED = "closed"
    REMOVED = "removed"


class ApplicationStatus:
    APPLIED = "applied"
    SELECTED = "selected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ShiftStatus:
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class PaymentStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class VerificationStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"