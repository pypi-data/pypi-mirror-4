from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


try:
    FACEBOOK_APP_ID = settings.FACEBOOK_APP_ID
except AttributeError:
    raise ImproperlyConfigured("Facebook app_id missing. Set FACEBOOK_APP_ID in settings.py")

try:
    FACEBOOK_APP_SECRET = settings.FACEBOOK_APP_SECRET
except AttributeError:
    raise ImproperlyConfigured("Facebook app_secret missing. Set FACEBOOK_APP_SECRET in settings.py")

try:
    EVENTS_FQL = settings.FACEBOOK_EVENTS_FQL
except AttributeError:
    EVENTS_FQL = """
        SELECT name, pic, start_time, end_time, location, description
        FROM event WHERE eid IN ( SELECT eid FROM event_member WHERE uid = %(uid)s )
        ORDER BY start_time asc
    """

try:
    NEWS_FQL = settings.FACEBOOK_NEWS_FQL
except AttributeError:
    NEWS_FQL = """
        SELECT post_id, actor_id, target_id, message
        FROM stream WHERE source_id = %(uid)s AND filter_key in (SELECT filter_key FROM stream_filter WHERE uid = %(uid)s AND type = 'newsfeed')
        ORDER BY updated_time asc
    """
    #11 - Group created
    #12 - Event created
    #46 - Status update
    #56 - Post on wall from another user
    #66 - Note created
    #80 - Link posted
    #128 -Video posted
    #247 - Photos posted
    #237 - App story
    #257 - Comment created
    #272 - App story
    #285 - Checkin to a place
    #308 - Post in Group
    NEWS_FQL = """
        SELECT
            action_links, actor_id, app_data, attribution, claim_count, comments,
            created_time, attachment,
            description, description_tags, expiration_timestamp, feed_targeting,
            filter_key, is_exportable, is_hidden, is_published, likes, message,
            message_tags, parent_post_id, permalink, place, post_id, promotion_status,
            scheduled_publish_time, share_count, source_id, tagged_ids, target_id,
            targeting, timeline_visibility, type, updated_time, via_id, viewer_id,
            with_location, with_tags, xid
        FROM stream WHERE source_id = %(uid)s AND type in (11, 12, 46, 66, 80, 128, 247, 237, 257, 272, 308)
        ORDER BY created_time desc
    """
