#!/usr/bin/env python3
import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("Poke-BFL Image Generation Server")

# Fal.ai API configuration
FAL_API_KEY = "f0f70e81-c5be-493d-8669-383edb142dfc:c884bec7933d703906f8ac7547b83235"
FAL_API_URL = "https://fal.run/fal-ai/flux-pro"

@mcp.tool(description="Generate an image using FLUX model via Fal.ai API. Returns image URL.")
def generate_image(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic") -> dict:
    """
    Generate an image from a text prompt using FLUX model.
    
    Args:
        prompt: Text description of the image to generate
        width: Image width in pixels (default: 1024)
        height: Image height in pixels (default: 1024)
        style: Image style - 'realistic', 'artistic', 'cartoon' (default: 'realistic')
    
    Returns:
        Dictionary with generation details and image URL
    """
    try:
        # Map dimensions to Fal.ai image_size parameter
        # For now, we'll use square_hd (1024x1024) as default
        image_size = "square_hd"  # Default to 1024x1024
        
        # Prepare API request
        headers = {
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 28,  # Default value
            "enable_safety_checker": True
        }
        
        # Make API call
        response = requests.post(FAL_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        if "images" in data and len(data["images"]) > 0:
            image_url = data["images"][0]["url"]
            return {
                "success": True,
                "message": "Image generated successfully!",
                "prompt": prompt,
                "parameters": {
                    "width": width,
                    "height": height,
                    "style": style,
                    "image_size": image_size
                },
                "image_url": image_url,
                "generation_id": f"flux_{hash(prompt) % 10000}",
                "note": "Image generated using FLUX Pro via Fal.ai"
            }
        else:
            return {
                "success": False,
                "message": "No image generated - API response was empty",
                "prompt": prompt,
                "error": "Empty response from Fal.ai API"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request failed: {str(e)}",
            "prompt": prompt,
            "error": f"Network/API error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "prompt": prompt,
            "error": f"Unexpected error: {str(e)}"
        }

@mcp.tool(description="Get information about the Poke-BFL MCP server and available tools")
def get_server_info() -> dict:
    return {
        "server_name": "Poke-BFL Image Generation Server",
        "version": "1.0.0",
        "description": "MCP server for FLUX image generation via Fal.ai API",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
        "available_tools": ["generate_image", "get_server_info"],
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
