from enum import Enum

class StatusEnum(str, Enum):
    pending = "pending"
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    incomplete = "incomplete"
    failed = "failed"
    rejected = "rejected"
    approved = "approved"

class ScheduleEnum(str,Enum):
    everyday="everyday"
    every_six_hours="every_six_hours"
    every_twelve_hours="every_twelve_hours"
    weekly="weekly"
    disabled="disabled"