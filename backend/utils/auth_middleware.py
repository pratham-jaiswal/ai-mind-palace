import os
import httpx
from functools import wraps
from flask import request, jsonify
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from svix.webhooks import Webhook

def require_signed_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sdk = Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY'))

        httpx_request = httpx.Request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            content=request.get_data()
        )

        request_state = sdk.authenticate_request(
            httpx_request,
            AuthenticateRequestOptions()
        )

        if not request_state.is_signed_in:
            return jsonify({"error": "Unauthorized"}), 401

        return func(*args, **kwargs)

    return wrapper

def clerk_webhook_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            raw_body = request.get_data(as_text=True)

            webhook = Webhook(os.getenv("CLERK_WEBHOOK_SECRET"))
            payload = webhook.verify(raw_body, request.headers)

            request.clerk_webhook_payload = payload

        except Exception as e:
            return jsonify({"error": f"Webhook verification failed: {str(e)}"}), 403

        return func(*args, **kwargs)
    return wrapper