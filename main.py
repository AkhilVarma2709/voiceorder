import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import get_supabase
from models import StatusUpdate, OrderStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voiceorder")

app = FastAPI(title="VoiceOrder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "VoiceOrder", "restaurant": "Swadeshi Frisco"}

@app.post("/debug")
async def debug_webhook(request: Request):
    data = await request.json()
    msg = data.get("message", data)
    msg_type = msg.get("type", "unknown")
    analysis = msg.get("analysis", {})
    structured = analysis.get("structuredData", {})
    call_data = msg.get("call", {})
    call_id = call_data.get("id", "")

    logger.info(f"=== VAPI WEBHOOK === type={msg_type} call_id={call_id}")
    logger.info(f"  analysis keys: {list(analysis.keys())}")
    logger.info(f"  structuredData: {json.dumps(structured, indent=2)}")

    # Log transcript summary (just messages, not word-level data)
    messages = msg.get("artifact", {}).get("messages", [])
    for m in messages:
        role = m.get("role", "?")
        text = m.get("message", m.get("content", ""))[:120]
        if role != "system":
            logger.info(f"  [{role}] {text}")

    return {"status": "ok", "type": msg_type, "structured_data": structured}


@app.post("/orders")
async def create_order(request: Request):
    try:
        body = await request.json()
        message = body.get("message", body)

        # Only process end-of-call reports
        if message.get("type") != "end-of-call-report":
            return {"status": "ignored", "reason": "not end-of-call-report"}

        # Extract structured data from analysis
        analysis = message.get("analysis", {})
        structured = analysis.get("structuredData", {})

        order_items = structured.get("order_items", "") or ""
        if not order_items.strip():
            return {"status": "ignored", "reason": "empty order_items"}

        # Extract customer phone and call id
        call_data = message.get("call", {})
        customer = call_data.get("customer", {})
        customer_phone = customer.get("number", "")
        call_id = call_data.get("id", "")

        order = {
            "restaurant_id": "swadeshi-frisco",
            "call_id": call_id,
            "customer_name": structured.get("customer_name", ""),
            "customer_phone": customer_phone,
            "order_items": order_items,
            "order_total": structured.get("order_total"),
            "special_instructions": structured.get("special_instructions", ""),
            "pickup_confirmed": structured.get("pickup_confirmed", False),
            "call_completed": structured.get("call_completed", False),
            "call_summary": structured.get("call_summary", ""),
            "status": "new",
        }

        logger.info(f"New order: {order['customer_name']} — {order['order_items']}")

        db = get_supabase()
        result = db.table("orders").insert(order).execute()

        order_id = result.data[0]["id"] if result.data else None
        return {"status": "received", "order_id": order_id}

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


@app.get("/orders")
async def list_orders(restaurant_id: str = "swadeshi-frisco"):
    try:
        db = get_supabase()
        result = (
            db.table("orders")
            .select("*")
            .eq("restaurant_id", restaurant_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


@app.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, body: StatusUpdate):
    try:
        db = get_supabase()
        result = (
            db.table("orders")
            .update({"status": body.status.value})
            .eq("id", order_id)
            .execute()
        )
        if not result.data:
            return JSONResponse(status_code=404, content={"status": "error", "detail": "Order not found"})
        return result.data[0]
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})
