#!/usr/bin/env python3
import os
import requests
import time
import threading
from fastmcp import FastMCP

mcp = FastMCP("Poke-BFL Image Generation Server")

# Fal.ai API configuration
FAL_API_KEY = "f0f70e81-c5be-493d-8669-383edb142dfc:c884bec7933d703906f8ac7547b83235"
FAL_API_URL = "https://fal.run/fal-ai/flux-pro"

# Simple in-memory storage for generation status
generation_status = {}

def _generate_image_async(generation_id: str, prompt: str, image_size: str):
    """Background function to generate image via Fal.ai API"""
    try:
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 28,
            "enable_safety_checker": True
        }
        
        response = requests.post(FAL_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if "images" in data and len(data["images"]) > 0:
            image_url = data["images"][0]["url"]
            # Update existing status instead of replacing it
            generation_status[generation_id].update({
                "status": "completed",
                "image_url": image_url,
                "success": True,
                "message": "Image generated successfully!"
            })
        else:
            generation_status[generation_id].update({
                "status": "failed",
                "success": False,
                "error": "Empty response from Fal.ai API"
            })
    except Exception as e:
        generation_status[generation_id].update({
            "status": "failed",
            "success": False,
            "error": str(e)
        })

@mcp.tool(description="Start image generation using FLUX model. Returns generation ID for status checking.")
def generate_image(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic") -> dict:
    """
    Start generating an image from a text prompt using FLUX model.
    
    Args:
        prompt: Text description of the image to generate
        width: Image width in pixels (default: 1024)
        height: Image height in pixels (default: 1024)
        style: Image style - 'realistic', 'artistic', 'cartoon' (default: 'realistic')
    
    Returns:
        Dictionary with generation ID and instructions to check status
    """
    generation_id = f"flux_{int(time.time())}_{hash(prompt) % 10000}"
    image_size = "square_hd"  # Default to 1024x1024
    
    # Initialize status
    generation_status[generation_id] = {
        "status": "processing",
        "prompt": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "style": style,
            "image_size": image_size
        },
        "started_at": time.time()
    }
    
    # Start background generation
    thread = threading.Thread(target=_generate_image_async, args=(generation_id, prompt, image_size))
    thread.daemon = True
    thread.start()
    
    return {
        "success": True,
        "message": "Image generation started! Use check_generation_status to get the result.",
        "generation_id": generation_id,
        "prompt": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "style": style,
            "image_size": image_size
        },
        "status": "processing",
        "note": "Generation takes 15-30 seconds. Check status with check_generation_status tool."
    }

@mcp.tool(description="Check the status of an image generation request")
def check_generation_status(generation_id: str) -> dict:
    """
    Check the status of an image generation request.
    
    Args:
        generation_id: The generation ID returned by generate_image
    
    Returns:
        Dictionary with current status and image URL if completed
    """
    if generation_id not in generation_status:
        return {
            "success": False,
            "message": "Generation ID not found",
            "error": f"No generation found with ID: {generation_id}"
        }
    
    status_info = generation_status[generation_id]
    
    if status_info["status"] == "processing":
        elapsed = time.time() - status_info["started_at"]
        return {
            "success": True,
            "status": "processing",
            "message": f"Image generation in progress... ({elapsed:.1f}s elapsed)",
            "generation_id": generation_id,
            "prompt": status_info["prompt"],
            "parameters": status_info["parameters"],
            "elapsed_seconds": round(elapsed, 1)
        }
    elif status_info["status"] == "completed":
        return {
            "success": True,
            "status": "completed",
            "message": "Image generated successfully!",
            "generation_id": generation_id,
            "prompt": status_info["prompt"],
            "parameters": status_info["parameters"],
            "image_url": status_info["image_url"],
            "note": "Image is ready! You can view it at the URL above."
        }
    else:  # failed
        return {
            "success": False,
            "status": "failed",
            "message": "Image generation failed",
            "generation_id": generation_id,
            "prompt": status_info["prompt"],
            "error": status_info["error"]
        }

@mcp.tool(description="Get information about the Poke-BFL MCP server and available tools")
def get_server_info() -> dict:
    return {
        "server_name": "Poke-BFL Image Generation Server",
        "version": "1.0.0",
        "description": "MCP server for FLUX image generation via Fal.ai API",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
        "available_tools": ["generate_image", "check_generation_status", "get_server_info"],
        "status": "Live - FLUX Pro integration via Fal.ai"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Poke-BFL MCP server on {host}:{port}")
    print("Server is running with live FLUX Pro integration - ready for testing with Poke!")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
