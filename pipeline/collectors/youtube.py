import os
import sys
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import SEED_PHRASES, DATE_WINDOW_MONTHS, RAW_DIR, YOUTUBE_DAILY_BUDGET
from pipeline.utils import setup_logger, save_checkpoint, load_checkpoint, append_jsonl, generate_id
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger("YouTubeCollector")

def collect_youtube_comments():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("YOUTUBE_API_KEY not found in env.")
        return
        
    youtube = build("youtube", "v3", developerKey=api_key)
    out_file = RAW_DIR / "youtube.jsonl"
    cutoff_date = datetime.now() - timedelta(days=DATE_WINDOW_MONTHS * 30)
    cutoff_iso = cutoff_date.isoformat() + "Z"
    
    checkpoint = load_checkpoint("youtube")
    quota_used = checkpoint.get("quota_used", 0)
    completed_queries = set(checkpoint.get("completed_queries", []))
    
    logger.info(f"Starting YouTube collection. Current quota used: {quota_used}")
    
    total_comments = 0
    
    for query in SEED_PHRASES:
        if query in completed_queries:
            continue
            
        if quota_used >= YOUTUBE_DAILY_BUDGET:
            logger.warning("Reached YouTube daily quota budget! Stopping for today.")
            break
            
        logger.info(f"Searching YouTube for: {query}")
        
        try:
            # search.list costs 100 units
            search_response = youtube.search().list(
                q=query,
                part="id",
                type="video",
                maxResults=50,
                publishedAfter=cutoff_iso
            ).execute()
            
            quota_used += 100
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            logger.info(f"Found {len(video_ids)} videos for query: {query}")
            
            for video_id in video_ids:
                if quota_used >= YOUTUBE_DAILY_BUDGET:
                    break
                    
                # commentThreads.list costs 1 unit
                try:
                    comments_response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100,
                        order="relevance"
                    ).execute()
                    
                    quota_used += 1
                    
                    for item in comments_response.get("items", []):
                        snippet = item["snippet"]["topLevelComment"]["snippet"]
                        dt_str = snippet["publishedAt"]
                        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        
                        if dt < cutoff_date:
                            continue
                            
                        comment = {
                            "id": generate_id("youtube", item["id"]),
                            "source": "youtube",
                            "country": "unknown",
                            "date": dt.isoformat(),
                            "text": snippet["textOriginal"],
                            "rating": None,
                            "metadata": {
                                "author": snippet.get("authorDisplayName"),
                                "likeCount": snippet.get("likeCount"),
                                "videoId": video_id,
                                "query": query
                            }
                        }
                        append_jsonl(out_file, comment)
                        total_comments += 1
                        
                except HttpError as e:
                    # Comments might be disabled for a video, ignore 403
                    if e.resp.status == 403:
                        pass
                    else:
                        logger.error(f"Error fetching comments for video {video_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error searching for query {query}: {e}")
            
        completed_queries.add(query)
        checkpoint["quota_used"] = quota_used
        checkpoint["completed_queries"] = list(completed_queries)
        save_checkpoint("youtube", checkpoint)
        
    logger.info(f"YouTube collection complete. Collected {total_comments} comments. Quota used: {quota_used}")

if __name__ == "__main__":
    collect_youtube_comments()
