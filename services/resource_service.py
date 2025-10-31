from repositories import VideoRepo

class ResourceService:
    def __init__(self, video_repo: VideoRepo):
        self.video_repo = video_repo
        
    def get_all_pending_videos(self, limit = 10):
        self.video_repo.
        