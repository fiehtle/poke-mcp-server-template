#!/usr/bin/env python3
import os
import requests
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables (for local development)
load_dotenv()

mcp = FastMCP("Poke-Attio CRM Integration")

# Attio API configuration
ATTIO_API_KEY = os.environ.get("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"

if not ATTIO_API_KEY:
    raise ValueError("ATTIO_API_KEY environment variable is required")

# Helper function to make Attio API requests
def make_attio_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """
    Make a request to Attio API with proper authentication
    
    Args:
        endpoint: API endpoint (e.g., '/self', '/objects/people/records/query')
        method: HTTP method (GET, POST, PATCH, DELETE)
        data: Request payload for POST/PATCH requests
    
    Returns:
        Response data as dictionary
    """
    url = f"{ATTIO_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {ATTIO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {response.status_code}: {response.text}"
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")

@mcp.tool(description="Search for a person/contact in Attio by name")
def search_person(name: str, limit: int = 10) -> dict:
    """
    Search for a person/contact in Attio CRM by name.
    Use this when asked questions like "What's the email of [person name]?"
    
    Args:
        name: Full or partial name of the person to search for
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary with search results including contact details
    """
    try:
        # Query people records
        query_data = {
            "filter": {
                "name": {
                    "$contains": name
                }
            },
            "limit": limit,
            "sorts": []
        }
        
        result = make_attio_request("/objects/people/records/query", method="POST", data=query_data)
        
        if not result.get("data"):
            return {
                "success": True,
                "found": False,
                "message": f"No person found with name containing '{name}'",
                "suggestion": "Try checking the spelling or using a different name variation"
            }
        
        # Format results
        people = []
        for record in result["data"]:
            person_info = {
                "id": record.get("id", {}).get("record_id"),
            }
            
            # Extract attributes (names, emails, etc.)
            values = record.get("values", {})
            for key, value_list in values.items():
                if value_list and len(value_list) > 0:
                    person_info[key] = value_list[0]
            
            people.append(person_info)
        
        return {
            "success": True,
            "found": True,
            "count": len(people),
            "message": f"Found {len(people)} person(s) matching '{name}'",
            "people": people
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search for person: {str(e)}"
        }

@mcp.tool(description="Search for a company in Attio by name")
def search_company(name: str, limit: int = 10) -> dict:
    """
    Search for a company in Attio CRM by name.
    
    Args:
        name: Full or partial name of the company to search for
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary with search results including company details
    """
    try:
        # Query company records
        query_data = {
            "filter": {
                "name": {
                    "$contains": name
                }
            },
            "limit": limit,
            "sorts": []
        }
        
        result = make_attio_request("/objects/companies/records/query", method="POST", data=query_data)
        
        if not result.get("data"):
            return {
                "success": True,
                "found": False,
                "message": f"No company found with name containing '{name}'",
                "suggestion": "Try checking the spelling or using a different name variation"
            }
        
        # Format results
        companies = []
        for record in result["data"]:
            company_info = {
                "id": record.get("id", {}).get("record_id"),
            }
            
            # Extract attributes
            values = record.get("values", {})
            for key, value_list in values.items():
                if value_list and len(value_list) > 0:
                    company_info[key] = value_list[0]
            
            companies.append(company_info)
        
        return {
            "success": True,
            "found": True,
            "count": len(companies),
            "message": f"Found {len(companies)} company(s) matching '{name}'",
            "companies": companies
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search for company: {str(e)}"
        }

@mcp.tool(description="Add a note to a person's record in Attio")
def add_note_to_person(person_name: str, note_content: str, note_title: str = "Note") -> dict:
    """
    Add a note to a person's record in Attio CRM.
    Use this when you want to attach notes (e.g., from Notion, meeting notes, call notes) to a contact.
    
    Args:
        person_name: Name of the person to add the note to
        note_content: The content of the note (can be from Notion or any other source)
        note_title: Title for the note (default: "Note")
    
    Returns:
        Dictionary with success status and note information
    """
    try:
        # First, search for the person
        search_result = search_person(person_name, limit=5)
        
        if not search_result.get("found") or not search_result.get("people"):
            return {
                "success": False,
                "message": f"Could not find person '{person_name}'. Please check the name and try again.",
                "suggestion": "Try searching for the person first to verify their name"
            }
        
        # If multiple matches, use the first one (could enhance to ask user to clarify)
        people = search_result["people"]
        if len(people) > 1:
            person_names = [p.get("name", {}).get("value", "Unknown") for p in people]
            return {
                "success": False,
                "message": f"Found {len(people)} people matching '{person_name}': {', '.join(person_names)}",
                "suggestion": "Please be more specific with the person's name",
                "matches": person_names
            }
        
        person = people[0]
        person_id = person.get("id")
        person_display_name = person.get("name", {}).get("value", person_name)
        
        if not person_id:
            return {
                "success": False,
                "message": "Found person but couldn't get their record ID",
                "error": "Missing person ID in search results"
            }
        
        # Create the note
        note_data = {
            "data": {
                "parent_object": "people",
                "parent_record_id": person_id,
                "title": note_title,
                "format": "plaintext",
                "content": note_content
            }
        }
        
        result = make_attio_request("/notes", method="POST", data=note_data)
        
        return {
            "success": True,
            "message": f"Successfully added note to {person_display_name}",
            "note": {
                "id": result.get("data", {}).get("id", {}).get("note_id"),
                "title": note_title,
                "attached_to": person_display_name,
                "parent_object": "people",
                "parent_record_id": person_id
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add note to person: {str(e)}"
        }

@mcp.tool(description="Add a note to a company's record in Attio")
def add_note_to_company(company_name: str, note_content: str, note_title: str = "Note") -> dict:
    """
    Add a note to a company's record in Attio CRM.
    Use this when you want to attach notes (e.g., from Notion, meeting notes, call notes) to a company.
    
    Args:
        company_name: Name of the company to add the note to
        note_content: The content of the note (can be from Notion or any other source)
        note_title: Title for the note (default: "Note")
    
    Returns:
        Dictionary with success status and note information
    """
    try:
        # First, search for the company
        search_result = search_company(company_name, limit=5)
        
        if not search_result.get("found") or not search_result.get("companies"):
            return {
                "success": False,
                "message": f"Could not find company '{company_name}'. Please check the name and try again.",
                "suggestion": "Try searching for the company first to verify their name"
            }
        
        # If multiple matches, use the first one (could enhance to ask user to clarify)
        companies = search_result["companies"]
        if len(companies) > 1:
            company_names = [c.get("name", {}).get("value", "Unknown") for c in companies]
            return {
                "success": False,
                "message": f"Found {len(companies)} companies matching '{company_name}': {', '.join(company_names)}",
                "suggestion": "Please be more specific with the company's name",
                "matches": company_names
            }
        
        company = companies[0]
        company_id = company.get("id")
        company_display_name = company.get("name", {}).get("value", company_name)
        
        if not company_id:
            return {
                "success": False,
                "message": "Found company but couldn't get their record ID",
                "error": "Missing company ID in search results"
            }
        
        # Create the note
        note_data = {
            "data": {
                "parent_object": "companies",
                "parent_record_id": company_id,
                "title": note_title,
                "format": "plaintext",
                "content": note_content
            }
        }
        
        result = make_attio_request("/notes", method="POST", data=note_data)
        
        return {
            "success": True,
            "message": f"Successfully added note to {company_display_name}",
            "note": {
                "id": result.get("data", {}).get("id", {}).get("note_id"),
                "title": note_title,
                "attached_to": company_display_name,
                "parent_object": "companies",
                "parent_record_id": company_id
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add note to company: {str(e)}"
        }

@mcp.tool(description="Get information about the Poke-Attio MCP server and available tools")
def get_server_info() -> dict:
    """
    Get information about the MCP server, workspace, and available tools.
    """
    try:
        # Get workspace info from Attio
        workspace_info = make_attio_request("/self")
        
        return {
            "server_name": "Poke-Attio CRM Integration",
            "version": "1.0.0",
            "description": "MCP server for Attio CRM - read and write CRM data via natural language",
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "python_version": os.sys.version.split()[0],
            "available_tools": ["search_person", "search_company", "add_note_to_person", "add_note_to_company", "get_server_info"],
            "status": "Live - Connected to Attio CRM",
            "workspace": {
                "name": workspace_info.get("workspace_name"),
                "id": workspace_info.get("workspace_id"),
                "active": workspace_info.get("active")
            },
            "permissions": workspace_info.get("scope", "").split()
        }
    except Exception as e:
        return {
            "server_name": "Poke-Attio CRM Integration",
            "version": "1.0.0",
            "description": "MCP server for Attio CRM",
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "available_tools": ["search_person", "search_company", "add_note_to_person", "add_note_to_company", "get_server_info"],
            "status": "Error connecting to Attio",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Poke-Attio MCP server on {host}:{port}")
    print("Server is running with live Attio CRM integration - ready for testing with Poke!")
    print(f"API Key configured: {'Yes' if ATTIO_API_KEY else 'No'}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
