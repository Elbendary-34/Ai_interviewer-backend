# LiveKit Server Integration
from livekit import api
from app.core.config import settings

class LiveKitService:
    def generate_token(self, room_name: str, participant_identity: str, participant_name: str = None) -> str:
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        token.with_identity(participant_identity)
        if participant_name:
            token.with_name(participant_name)

        # Grant room permissions (join room & allow sending audio/video)
        grant = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        )
        token.with_grants(grant)

        return token.to_jwt()

livekit_service = LiveKitService()