from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DYNAMODB_VIDEOS_TABLE = os.getenv("DYNAMODB_VIDEOS_TABLE", "guardian-videos")
DYNAMODB_EVENTS_TABLE = os.getenv("DYNAMODB_EVENTS_TABLE", "guardian-events")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "guardian-videos")

# AWS Clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
videos_table = dynamodb.Table(DYNAMODB_VIDEOS_TABLE)
events_table = dynamodb.Table(DYNAMODB_EVENTS_TABLE)

# Helper function to convert Decimal to float
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@app.get("/videos")
async def get_all_videos(status: Optional[str] = None, limit: int = 100):
    """Get all videos, optionally filtered by status"""
    try:
        if status:
            response = videos_table.scan(
                FilterExpression="#status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": status},
                Limit=limit
            )
        else:
            response = videos_table.scan(Limit=limit)
        
        items = response.get('Items', [])
        
        # Convert Decimal to float for JSON serialization
        items_json = json.loads(json.dumps(items, default=decimal_to_float))
        
        # Sort by uploaded_at (newest first)
        items_json.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
        
        return items_json
    except ClientError as e:
        raise HTTPException(500, f"Failed to fetch videos: {str(e)}")

@app.get("/videos/{video_id}")
async def get_video_by_id(video_id: str):
    """Get video details by ID"""
    try:
        response = videos_table.get_item(Key={"video_id": video_id})
        
        if 'Item' not in response:
            raise HTTPException(404, "Video not found")
        
        item = response['Item']
        
        # Convert Decimal to float for JSON serialization
        item_json = json.loads(json.dumps(item, default=decimal_to_float))
        
        return item_json
    except ClientError as e:
        raise HTTPException(500, f"Failed to fetch video: {str(e)}")

@app.get("/videos/{video_id}/stream")
async def stream_video(video_id: str):
    """Return a presigned URL for streaming the video from S3."""
    try:
        response = videos_table.get_item(Key={"video_id": video_id})
        if 'Item' not in response:
            raise HTTPException(404, "Video not found")

        item = response['Item']
        s3_key = item.get("s3_key") or f"videos/{video_id}.mp4"

        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=3600
        )

        return RedirectResponse(url=url)
    except ClientError as e:
        raise HTTPException(500, f"Failed to generate stream URL: {str(e)}")

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Scan all videos
        response = videos_table.scan()
        items = response.get('Items', [])
        
        # Calculate statistics
        stats = {
            "total": len(items),
            "approved": len([v for v in items if v.get('status') == 'approved']),
            "rejected": len([v for v in items if v.get('status') == 'rejected']),
            "pending_review": len([v for v in items if v.get('status') == 'review']),
            "processing": len([v for v in items if v.get('status') in ['uploaded', 'screened', 'analyzed', 'processing']]),
        }
        
        return stats
    except ClientError as e:
        raise HTTPException(500, f"Failed to fetch stats: {str(e)}")

@app.get("/events/{video_id}")
async def get_video_events(video_id: str):
    """Get all events for a specific video"""
    try:
        response = events_table.scan(
            FilterExpression="video_id = :vid",
            ExpressionAttributeValues={":vid": video_id}
        )
        
        items = response.get('Items', [])
        
        # Convert Decimal to float and sort by timestamp
        items_json = json.loads(json.dumps(items, default=decimal_to_float))
        items_json.sort(key=lambda x: x.get('timestamp', ''))
        
        return items_json
    except ClientError as e:
        raise HTTPException(500, f"Failed to fetch events: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test DynamoDB connection
        videos_table.table_status
        return {
            "status": "healthy",
            "service": "api-gateway",
            "dynamodb": "connected"
        }
    except Exception as e:
        raise HTTPException(503, f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
