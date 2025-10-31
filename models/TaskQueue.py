from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    Pending = "PENDING"
    Running = "RUNNING"
    Completed = "COMPLETED"
    ERROR = "ERROR"

class VideoJob(BaseModel):
    id: str
    video_id: str
