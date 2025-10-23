#!/usr/bin/env python3
import os
import requests
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables (for local development)
load_dotenv()

mcp = FastMCP("Poke-Attio CRM Integration")

# Attio API configuration - API key will be passed by Poke client
ATTIO_API_KEY = None  # Will be set dynamically by Poke client
ATTIO_BASE_URL = "https://api.attio.com/v2"

# Note: API key validation moved to make_attio_request function

# Helper function to make Attio API requests
def make_attio_request(endpoint: str, method: str = "GET", data: dict = None, api_key: str = None) -> dict:
    """
    Make a request to Attio API with proper authentication
    
    Args:
        endpoint: API endpoint (e.g., '/self', '/objects/people/records/query')
        method: HTTP method (GET, POST, PATCH, DELETE)
        data: Request payload for POST/PATCH requests
        api_key: Attio API key (passed by Poke client or from environment)
    
    Returns:
        Response data as dictionary
    """
    if not api_key:
        # Try to get from environment (for Poke configuration)
        api_key = os.environ.get("ATTIO_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Please configure it in Poke's integration settings or set ATTIO_API_KEY environment variable.")
    
    url = f"{ATTIO_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
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

# ============================================================================
# DISCOVERY TOOLS - Let Poke discover what's possible in Attio
# ============================================================================

@mcp.tool(description="List all available object types in Attio workspace")
def list_available_objects(api_key: str = None) -> dict:
    """
    Get a list of all object types available in your Attio workspace.
    Use this to discover what objects you can query (people, companies, deals, etc.)
    
    Returns:
        Dictionary with list of available object types and their metadata
    """
    try:
        result = make_attio_request("/objects", api_key=api_key)
        
        if not result.get("data"):
            return {
                "success": True,
                "objects": [],
                "message": "No objects found in workspace"
            }
        
        # Extract object types and metadata
        objects = []
        for obj in result["data"]:
            objects.append({
                "api_slug": obj.get("api_slug"),  # e.g., "people", "companies"
                "singular_noun": obj.get("singular_noun"),  # e.g., "Person", "Company"
                "plural_noun": obj.get("plural_noun"),  # e.g., "People", "Companies"
                "id": obj.get("id", {}).get("object_id")
            })
        
        return {
            "success": True,
            "count": len(objects),
            "objects": objects,
            "message": f"Found {len(objects)} object types in workspace"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list objects: {str(e)}"
        }

@mcp.tool(description="Get schema/attributes for a specific object type in Attio")
def get_object_schema(object_type: str, api_key: str = None) -> dict:
    """
    Get the schema and available attributes for a specific object type.
    This tells you what fields you can query, filter, and update.
    
    Args:
        object_type: The object type (e.g., "people", "companies", "deals")
                    Use list_available_objects() to see valid types
    
    Returns:
        Dictionary with object schema including all attributes and their types
    """
    try:
        # Get object attributes
        result = make_attio_request(f"/objects/{object_type}/attributes", api_key=api_key)
        
        if not result.get("data"):
            return {
                "success": False,
                "message": f"No attributes found for object type '{object_type}'",
                "suggestion": "Check the object_type spelling or use list_available_objects() to see valid types"
            }
        
        # Extract attribute information
        attributes = {}
        for attr in result["data"]:
            attr_slug = attr.get("api_slug")
            attributes[attr_slug] = {
                "title": attr.get("title"),
                "type": attr.get("type"),
                "is_required": attr.get("is_required", False),
                "is_unique": attr.get("is_unique", False),
                "is_multiselect": attr.get("is_multiselect", False),
                "description": attr.get("description")
            }
        
        return {
            "success": True,
            "object_type": object_type,
            "attribute_count": len(attributes),
            "attributes": attributes,
            "message": f"Found {len(attributes)} attributes for {object_type}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get schema for '{object_type}': {str(e)}",
            "suggestion": "Use list_available_objects() to see valid object types"
        }

# ============================================================================
# UNIVERSAL QUERY TOOL - Query ANY object with ANY filters
# ============================================================================

@mcp.tool(description="Query Attio records with advanced filtering (supports ANY object type and ANY attributes)")
def query_records(object_type: str, api_key: str = None, filters: dict = None, limit: int = 50, sorts: list = None) -> dict:
    """
    Universal query tool for Attio CRM. Query ANY object type with ANY filters.
    This replaces specific search tools and supports advanced use cases.
    
    Examples:
    - Search by name: query_records("people", {"name": {"$contains": "John"}})
    - Find event attendees: query_records("people", {"events_attended": {"$contains": "TechConf 2024"}})
    - Find by location: query_records("companies", {"location": {"$eq": "Austin"}})
    - Find by tags: query_records("companies", {"tags": {"$contains": "VIP"}})
    - Complex filters: query_records("deals", {"value": {"$gt": 100000}, "status": {"$eq": "open"}})
    
    Filter operators:
    - $eq: equals
    - $contains: contains (for text and arrays)
    - $gt, $lt, $gte, $lte: greater/less than (for numbers/dates)
    - See Attio API docs for full list
    
    Args:
        object_type: Object type to query (use list_available_objects() to see options)
        filters: Dictionary of filters (use get_object_schema() to see available attributes)
        limit: Maximum number of records to return (default: 50)
        sorts: List of sort specifications (optional)
    
    Returns:
        Dictionary with matching records and their attributes
    """
    try:
        # Build query payload
        query_data = {
            "limit": limit
        }
        
        if filters:
            query_data["filter"] = filters
        
        if sorts:
            query_data["sorts"] = sorts
        
        # Make the query
        result = make_attio_request(f"/objects/{object_type}/records/query", method="POST", data=query_data, api_key=api_key)
        
        if not result.get("data"):
            return {
                "success": True,
                "found": False,
                "count": 0,
                "records": [],
                "message": f"No {object_type} found matching the filters",
                "filters_used": filters
            }
        
        # Format results
        records = []
        for record in result["data"]:
            record_info = {
                "id": record.get("id", {}).get("record_id"),
            }
            
            # Extract all attributes
            values = record.get("values", {})
            for key, value_list in values.items():
                if value_list and len(value_list) > 0:
                    # Get the actual value from the first item
                    record_info[key] = value_list[0]
            
            records.append(record_info)
        
        return {
            "success": True,
            "found": True,
            "count": len(records),
            "object_type": object_type,
            "records": records,
            "message": f"Found {len(records)} {object_type} matching the filters",
            "filters_used": filters
        }
    
    except Exception as e:
        error_str = str(e)
        suggestion = ""
        
        # Provide helpful suggestions based on error
        if "404" in error_str or "not found" in error_str.lower():
            suggestion = f"Object type '{object_type}' may not exist. Use list_available_objects() to see valid types."
        elif "400" in error_str or "bad request" in error_str.lower():
            suggestion = "Filter syntax may be incorrect. Use get_object_schema() to see valid attributes."
        
        return {
            "success": False,
            "error": error_str,
            "message": f"Failed to query {object_type}: {error_str}",
            "suggestion": suggestion,
            "filters_used": filters
        }

# ============================================================================
# LIST MANAGEMENT TOOLS - Manage list entries and memberships
# ============================================================================

@mcp.tool(description="List all available lists in your Attio workspace")
def list_all_lists() -> dict:
    """
    List all available lists in your Attio workspace.
    
    Use this to discover what lists exist before querying them.
    
    Returns:
        Dictionary with all lists and their metadata
    """
    try:
        result = make_attio_request("/lists")
        
        if not result.get("data"):
            return {
                "success": True,
                "lists": [],
                "message": "No lists found in workspace"
            }
        
        # Format lists
        lists = []
        for list_obj in result["data"]:
            lists.append({
                "id": list_obj.get("id", {}).get("list_id"),
                "name": list_obj.get("name"),
                "api_slug": list_obj.get("api_slug"),
                "parent_object": list_obj.get("parent_object", []),
                "created_at": list_obj.get("created_at"),
                "workspace_access": list_obj.get("workspace_access")
            })
        
        return {
            "success": True,
            "count": len(lists),
            "lists": lists,
            "message": f"Found {len(lists)} lists in workspace"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list lists: {str(e)}"
        }

# Internal helper function for get_list_entries logic
def _get_list_entries_internal(list_identifier: str, api_key: str = None, filters: dict = None, limit: int = 50) -> dict:
    """
    Internal helper function for get_list_entries logic.
    Used by other functions that need to call get_list_entries without MCP wrapper.
    """
    try:
        # First, try to find the list by name if identifier is not a UUID
        list_id = list_identifier
        list_name = list_identifier
        
        if "-" not in list_identifier or len(list_identifier) < 30:
            # Probably a name, search for the list using the /lists endpoint
            lists_result = make_attio_request("/lists", api_key=api_key)
            
            if not lists_result.get("data"):
                return {
                    "success": False,
                    "message": f"No lists found in workspace",
                    "suggestion": "Check if lists exist in your Attio workspace"
                }
            
            # Find matching list by name
            matching_lists = []
            for list_obj in lists_result["data"]:
                if list_identifier.lower() in list_obj.get("name", "").lower():
                    matching_lists.append(list_obj)
            
            if not matching_lists:
                available_names = [l.get("name", "Unknown") for l in lists_result["data"]]
                return {
                    "success": False,
                    "message": f"Could not find list matching '{list_identifier}'",
                    "available_lists": available_names,
                    "suggestion": "Use one of the available list names"
                }
            
            if len(matching_lists) > 1:
                list_names = [l.get("name", "Unknown") for l in matching_lists]
                return {
                    "success": False,
                    "message": f"Found {len(matching_lists)} lists matching '{list_identifier}': {', '.join(list_names)}",
                    "suggestion": "Be more specific or use the list ID directly"
                }
            
            list_obj = matching_lists[0]
            list_id = list_obj.get("id", {}).get("list_id")
            list_name = list_obj.get("name", list_identifier)
        
        # Query list entries
        query_data = {"limit": limit}
        if filters:
            query_data["filter"] = filters
        
        result = make_attio_request(f"/lists/{list_id}/entries/query", method="POST", data=query_data, api_key=api_key)
        
        if not result.get("data"):
            return {
                "success": True,
                "found": False,
                "count": 0,
                "list_name": list_name,
                "entries": [],
                "message": f"No entries found in list '{list_name}'" + (f" matching filters" if filters else "")
            }
        
        # Format entries
        entries = []
        for entry in result["data"]:
            entry_info = {
                "entry_id": entry.get("id", {}).get("entry_id"),
                "record_id": entry.get("parent_record_id"),
            }
            
            # Extract entry values (list-specific attributes like status)
            entry_values = entry.get("entry_values", {})
            for key, value_list in entry_values.items():
                if value_list and len(value_list) > 0:
                    entry_info[key] = value_list[0]
            
            # Also include parent record values if available
            if "parent_record" in entry:
                values = entry["parent_record"].get("values", {})
                for key, value_list in values.items():
                    if value_list and len(value_list) > 0:
                        entry_info[f"record_{key}"] = value_list[0]
            
            entries.append(entry_info)
        
        return {
            "success": True,
            "found": True,
            "count": len(entries),
            "list_name": list_name,
            "list_id": list_id,
            "entries": entries,
            "message": f"Found {len(entries)} entries in list '{list_name}'"
        }
    
    except Exception as e:
        error_str = str(e)
        
        # Provide helpful guidance for status filtering errors
        if "unknown_filter_status_slug" in error_str or "Unknown status" in error_str:
            return {
                "success": False,
                "error": error_str,
                "message": f"Status filtering error: {error_str}",
                "suggestion": "Status filtering requires status IDs, not display names. Use get_list_statuses() to find available statuses and their IDs.",
                "help": {
                    "tool": "get_list_statuses",
                    "description": "Call get_list_statuses('list_name') to see all available statuses with their IDs",
                    "example": "get_list_statuses('LP Fundraising')"
                }
            }
        elif "invalid_filter_operator" in error_str:
            return {
                "success": False,
                "error": error_str,
                "message": f"Filter operator error: {error_str}",
                "suggestion": "Status fields only support '$eq' operator. Use exact status ID matches.",
                "help": {
                    "correct_format": {"status": {"$eq": "status_id_here"}},
                    "incorrect_format": {"status": {"$contains": "status_name"}}
                }
            }
        
        return {
            "success": False,
            "error": error_str,
            "message": f"Failed to get list entries: {error_str}"
        }

@mcp.tool(description="Get all available statuses for a specific list with their IDs and display names")
def get_list_statuses(list_identifier: str, api_key: str = None) -> dict:
    """
    Get all available statuses for a specific list in Attio.
    
    This tool helps you discover what statuses are available for filtering.
    Use the returned status IDs in get_list_entries() filters.
    
    Args:
        list_identifier: List name or ID (e.g., "LP Fundraising")
    
    Returns:
        Dictionary with all available statuses and their IDs
    """
    try:
        # First, get a sample of entries to extract status information
        # We need to call the underlying function directly, not the MCP tool
        sample_result = _get_list_entries_internal(list_identifier, api_key=api_key, limit=100)
        
        if not sample_result.get("success"):
            return sample_result
        
        if not sample_result.get("found"):
            return {
                "success": True,
                "list_name": sample_result.get("list_name", list_identifier),
                "statuses": [],
                "message": f"No entries found in list '{list_identifier}' to determine statuses"
            }
        
        # Extract unique statuses from entries
        statuses = {}
        for entry in sample_result["entries"]:
            if "status" in entry and "status" in entry["status"]:
                status_info = entry["status"]["status"]
                status_id = status_info["id"]["status_id"]
                status_title = status_info["title"]
                
                if status_id not in statuses:
                    statuses[status_id] = {
                        "id": status_id,
                        "title": status_title,
                        "is_archived": status_info.get("is_archived", False),
                        "example_entry_count": 1
                    }
                else:
                    statuses[status_id]["example_entry_count"] += 1
        
        # Convert to list and sort by title
        status_list = list(statuses.values())
        status_list.sort(key=lambda x: x["title"])
        
        return {
            "success": True,
            "list_name": sample_result.get("list_name", list_identifier),
            "list_id": sample_result.get("list_id"),
            "count": len(status_list),
            "statuses": status_list,
            "message": f"Found {len(status_list)} unique statuses in list '{sample_result.get('list_name', list_identifier)}'",
            "usage_example": {
                "description": "Use status IDs in get_list_entries filters",
                "example": f"get_list_entries('{list_identifier}', {{'status': {{'$eq': '{status_list[0]['id'] if status_list else 'status_id_here'}'}}}})"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get list statuses: {str(e)}"
        }

@mcp.tool(description="Get entries from a specific list in Attio with optional filtering. IMPORTANT: For status filtering, use status IDs not display names (use get_list_statuses to find them)")
def get_list_entries(list_identifier: str, api_key: str = None, filters: dict = None, limit: int = 50) -> dict:
    """
    Get entries from a specific list in Attio with optional filtering.
    
    Use this to query people/companies within a specific list (e.g., "LP fundraising").
    You can filter by list-specific attributes like status.
    
    Examples:
    - Get all entries: get_list_entries("LP fundraising")
    - Filter by status ID: get_list_entries("LP fundraising", {"status": {"$eq": "c8fb3791-8a5c-4092-85b9-56ea1503db04"}})
    
    Args:
        list_identifier: List name or ID (try name first, e.g., "LP fundraising")
        filters: Optional filters for list-specific attributes (use status IDs, not display names)
        limit: Maximum entries to return (default: 50)
    
    Returns:
        Dictionary with list entries and their attributes
    """
    return _get_list_entries_internal(list_identifier, api_key, filters, limit)

@mcp.tool(description="Update attributes of a list entry (e.g., change status)")
def update_list_entry(list_identifier: str, person_identifier: str, attribute_updates: dict, api_key: str = None) -> dict:
    """
    Update list-specific attributes for a person in a list (e.g., change their status).
    
    Use this to update list membership attributes like status, stage, priority, etc.
    
    Examples:
    - Update status: update_list_entry("LP fundraising", "john@example.com", {"status": "committed"})
    - Update multiple: update_list_entry("LP fundraising", "Jane Smith", {"status": "declined", "notes": "..."})
    
    Args:
        list_identifier: List name or ID
        person_identifier: Person's name or email
        attribute_updates: Dictionary of attributes to update (e.g., {"status": "new value"})
    
    Returns:
        Dictionary with update confirmation
    """
    try:
        # Get the list entries to find the entry_id
        entries_result = get_list_entries(list_identifier, api_key=api_key, limit=100)
        
        if not entries_result.get("success"):
            return entries_result
        
        if not entries_result.get("found"):
            return {
                "success": False,
                "message": f"List '{list_identifier}' has no entries"
            }
        
        # Find the person in the list entries
        target_entry = None
        for entry in entries_result["entries"]:
            # Check email or name
            record_email = entry.get("record_email_addresses", {}).get("value", "")
            record_name = entry.get("record_name", {}).get("value", "")
            
            if (person_identifier.lower() in record_email.lower() or 
                person_identifier.lower() in record_name.lower()):
                target_entry = entry
                break
        
        if not target_entry:
            return {
                "success": False,
                "message": f"Could not find '{person_identifier}' in list '{list_identifier}'",
                "suggestion": f"Use get_list_entries('{list_identifier}') to see who's in the list"
            }
        
        entry_id = target_entry.get("entry_id")
        list_id = entries_result.get("list_id")
        
        # Update the entry
        update_data = {
            "data": {
                "entry_values": attribute_updates
            }
        }
        
        result = make_attio_request(f"/lists/{list_id}/entries/{entry_id}", method="PUT", data=update_data, api_key=api_key)
        
        return {
            "success": True,
            "message": f"Successfully updated {person_identifier} in list '{entries_result.get('list_name')}'",
            "updated_attributes": attribute_updates,
            "entry_id": entry_id
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update list entry: {str(e)}"
        }

@mcp.tool(description="Add one or more people to an Attio list (supports bulk)")
def add_to_list(list_identifier: str, person_identifiers: list, entry_attributes: dict = None, api_key: str = None) -> dict:
    """
    Add one or more people to a list. Supports bulk additions!
    
    Use this to add people to lists like "LP fundraising", "VIP Customers", etc.
    You can also set initial list-specific attributes like status.
    
    Examples:
    - Add one: add_to_list("LP fundraising", ["john@example.com"], {"status": "initial contact"})
    - Bulk add: add_to_list("LP fundraising", ["a@e.com", "b@e.com", "c@e.com"], {"status": "intro"})
    
    Args:
        list_identifier: List name or ID
        person_identifiers: List of names or emails to add
        entry_attributes: Optional attributes to set (e.g., {"status": "new"})
    
    Returns:
        Dictionary with results for each person added
    """
    try:
        # Get list ID
        if "-" not in list_identifier or len(list_identifier) < 30:
            # Search for the list using the /lists endpoint
            lists_result = make_attio_request("/lists", api_key=api_key)
            
            if not lists_result.get("data"):
                return {
                    "success": False,
                    "message": f"No lists found in workspace"
                }
            
            # Find matching list by name
            matching_lists = []
            for list_obj in lists_result["data"]:
                if list_identifier.lower() in list_obj.get("name", "").lower():
                    matching_lists.append(list_obj)
            
            if not matching_lists:
                available_names = [l.get("name", "Unknown") for l in lists_result["data"]]
                return {
                    "success": False,
                    "message": f"Could not find list '{list_identifier}'",
                    "available_lists": available_names
                }
            
            list_obj = matching_lists[0]
            list_id = list_obj.get("id", {}).get("list_id")
            list_name = list_obj.get("name", list_identifier)
        else:
            list_id = list_identifier
            list_name = list_identifier
        
        # Find each person and add to list
        results = []
        for person_id in person_identifiers:
            try:
                # Search for person
                search_result = query_records(
                    "people",
                    api_key=api_key,
                    filters={"name": {"$contains": person_id}} if "@" not in person_id 
                    else {"email_addresses": {"$contains": person_id}},
                    limit=1
                )
                
                if not search_result.get("found"):
                    results.append({
                        "identifier": person_id,
                        "success": False,
                        "message": f"Person not found"
                    })
                    continue
                
                person_record_id = search_result["records"][0].get("id")
                
                # Add to list
                add_data = {
                    "data": {
                        "parent_record_id": person_record_id
                    }
                }
                
                if entry_attributes:
                    add_data["data"]["entry_values"] = entry_attributes
                
                make_attio_request(f"/lists/{list_id}/entries", method="POST", data=add_data, api_key=api_key)
                
                results.append({
                    "identifier": person_id,
                    "success": True,
                    "message": "Added to list"
                })
            
            except Exception as e:
                results.append({
                    "identifier": person_id,
                    "success": False,
                    "message": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "list_name": list_name,
            "total_attempted": len(person_identifiers),
            "successful": success_count,
            "failed": len(person_identifiers) - success_count,
            "results": results,
            "message": f"Added {success_count}/{len(person_identifiers)} people to '{list_name}'"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add to list: {str(e)}"
        }

# ============================================================================
# LEGACY SPECIFIC SEARCH TOOLS (Kept for backward compatibility)
# Prefer using query_records() for more flexibility
# ============================================================================

@mcp.tool(description="[LEGACY] Search for a person/contact in Attio by name - Consider using query_records() instead")
def search_person(name: str, limit: int = 10, api_key: str = None) -> dict:
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
        
        result = make_attio_request("/objects/people/records/query", method="POST", data=query_data, api_key=api_key)
        
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

@mcp.tool(description="[LEGACY] Search for a company in Attio by name - Consider using query_records() instead")
def search_company(name: str, limit: int = 10, api_key: str = None) -> dict:
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
        
        result = make_attio_request("/objects/companies/records/query", method="POST", data=query_data, api_key=api_key)
        
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

# ============================================================================
# UNIVERSAL NOTE CREATION TOOL - Create notes for ANY object type
# ============================================================================

@mcp.tool(description="Create a note and attach it to any Attio record (person, company, deal, etc.)")
def create_note(parent_object: str, parent_identifier: str, content: str, title: str = "Note", api_key: str = None) -> dict:
    """
    Universal note creation tool. Create a note and attach it to ANY object type.
    This replaces specific note tools (add_note_to_person, add_note_to_company, etc.)
    
    Examples:
    - Add note to person: create_note("people", "John Smith", "Call notes from meeting...", "Meeting Notes")
    - Add note to company: create_note("companies", "Acme Corp", "Partnership discussion...", "Partnership Notes")
    - Add note to deal: create_note("deals", "Q4 Deal", "Updated terms...", "Deal Update")
    
    Args:
        parent_object: Object type (use list_available_objects() to see options)
        parent_identifier: Name or ID of the record to attach note to
        content: The note content (can be from Notion, meeting notes, etc.)
        title: Title for the note (default: "Note")
    
    Returns:
        Dictionary with success status and note information
    """
    try:
        # Determine if identifier is an ID or name
        # If it looks like a record ID (UUID format), use it directly
        # Otherwise, search for the record by name
        
        parent_record_id = None
        display_name = parent_identifier
        
        # Simple heuristic: if it contains hyphens and is long, probably an ID
        if "-" in parent_identifier and len(parent_identifier) > 30:
            parent_record_id = parent_identifier
        else:
            # Search for the record by name
            search_result = query_records(
                object_type=parent_object,
                api_key=api_key,
                filters={"name": {"$contains": parent_identifier}},
                limit=5
            )
            
            if not search_result.get("found") or not search_result.get("records"):
                return {
                    "success": False,
                    "message": f"Could not find {parent_object} matching '{parent_identifier}'",
                    "suggestion": f"Try query_records('{parent_object}', {{'name': {{'$contains': '...'}}}}) to find the correct name"
                }
            
            records = search_result["records"]
            if len(records) > 1:
                record_names = [r.get("name", {}).get("value", "Unknown") for r in records]
                return {
                    "success": False,
                    "message": f"Found {len(records)} {parent_object} matching '{parent_identifier}': {', '.join(record_names)}",
                    "suggestion": "Please be more specific with the name, or provide the record ID directly",
                    "matches": record_names
                }
            
            record = records[0]
            parent_record_id = record.get("id")
            display_name = record.get("name", {}).get("value", parent_identifier)
        
        if not parent_record_id:
            return {
                "success": False,
                "message": f"Could not determine record ID for '{parent_identifier}'",
                "error": "Missing record ID"
            }
        
        # Create the note
        note_data = {
            "data": {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
                "title": title,
                "format": "plaintext",
                "content": content
            }
        }
        
        result = make_attio_request("/notes", method="POST", data=note_data, api_key=api_key)
        
        return {
            "success": True,
            "message": f"Successfully added note '{title}' to {parent_object} '{display_name}'",
            "note": {
                "id": result.get("data", {}).get("id", {}).get("note_id"),
                "title": title,
                "attached_to": display_name,
                "parent_object": parent_object,
                "parent_record_id": parent_record_id
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create note: {str(e)}",
            "suggestion": "Use list_available_objects() to see valid object types"
        }

# ============================================================================
# LEGACY NOTE TOOLS (Kept for backward compatibility)
# Prefer using create_note() for more flexibility
# ============================================================================

@mcp.tool(description="[LEGACY] Add a note to a person's record in Attio - Consider using create_note() instead")
def add_note_to_person(person_name: str, note_content: str, note_title: str = "Note", api_key: str = None) -> dict:
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
        search_result = search_person(person_name, limit=5, api_key=api_key)
        
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
        
        result = make_attio_request("/notes", method="POST", data=note_data, api_key=api_key)
        
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

@mcp.tool(description="[LEGACY] Add a note to a company's record in Attio - Consider using create_note() instead")
def add_note_to_company(company_name: str, note_content: str, note_title: str = "Note", api_key: str = None) -> dict:
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
        search_result = search_company(company_name, limit=5, api_key=api_key)
        
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
        
        result = make_attio_request("/notes", method="POST", data=note_data, api_key=api_key)
        
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

@mcp.tool(description="Get information about the MCP server, workspace, and available tools")
def get_server_info(api_key: str = None) -> dict:
    """
    Get information about the MCP server, workspace, and available tools.
    """
    try:
        # Get workspace info from Attio
        workspace_info = make_attio_request("/self", api_key=api_key)
        
        return {
            "server_name": "Poke-Attio CRM Integration",
            "version": "2.0.0",
            "description": "MCP server for Attio CRM - Generic tools for ANY object type and ANY filters",
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "python_version": os.sys.version.split()[0],
            "available_tools": {
                "recommended": [
                    "list_available_objects - Discover what objects exist",
                    "get_object_schema - See available attributes for an object",
                    "query_records - Query ANY object with ANY filters",
                    "create_note - Add notes to ANY object type",
                    "list_all_lists - List all available lists in workspace",
                    "get_list_statuses - Get available statuses for a list (with IDs)",
                    "get_list_entries - Get entries from a list with filtering",
                    "update_list_entry - Update list entry attributes (status, etc.)",
                    "add_to_list - Add people to lists (bulk supported)",
                    "get_server_info - Server status"
                ],
                "legacy": [
                    "search_person - Use query_records() instead",
                    "search_company - Use query_records() instead",
                    "add_note_to_person - Use create_note() instead",
                    "add_note_to_company - Use create_note() instead"
                ]
            },
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
            "version": "2.0.0",
            "description": "MCP server for Attio CRM - Generic tools for ANY object type and ANY filters",
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "available_tools": ["list_available_objects", "get_object_schema", "query_records", "create_note", "get_server_info"],
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
