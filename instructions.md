# Attio MCP Server Project Instructions

## Project Overview
**Project Name:** Attio MCP Server (Poke + Attio CRM Integration)  
**Purpose:** Create an MCP integration that allows Poke AI assistant to serve as a natural language UI layer on top of Attio CRM  
**Type:** MCP Server Integration  
**Context:** Enable seamless reading and writing of CRM data through conversational interactions with Poke, eliminating the need to context-switch to Attio's web interface for common operations.

## Project Goals
- Enable Poke to query and retrieve CRM data from Attio using natural language
- Provide write capabilities for updating records and adding notes to Attio
- Create reusable, modular MCP tools for CRM operations
- Allow users to interact with their CRM through conversational queries like "What's the email of [contact name]?"
- Build a foundation that can be extended with real-time features (webhooks) in the future

## Target Audience
- Business professionals who use Attio CRM and want faster access to CRM data
- Teams who prefer conversational interfaces over traditional CRM UIs
- Users who want to quickly lookup contact info, add notes, or update records without leaving their workflow

## Core Features
- **Contact Search:** Find people/contacts by name and retrieve their details (email, phone, etc.)
- **Company Lookup:** Search and retrieve company information
- **Deal Management:** Access deal information and status
- **Notes Management:** Add notes to records (e.g., "Add call notes from Notion to Attio")
- **Record Updates:** Update existing records with new information
- **List Queries:** Query lists with filters and sorting
- **Error Handling:** Robust error handling and user-friendly error messages
- **API Integration:** Direct REST API integration with Attio
- **MCP Protocol:** Full MCP compliance for Poke integration

## Technical Requirements
### Technology Stack
- **MCP Server:** Python with FastMCP framework
- **API Integration:** Attio REST API v2
- **Deployment:** Render (streamable HTTP transport)
- **Protocol:** MCP (Model Context Protocol)
- **Authentication:** API Key (Bearer token)

### API Details
- **Base URL:** `https://api.attio.com/v2/`
- **Authentication:** Bearer token in `Authorization` header
- **Data Format:** JSON over HTTPS
- **Standard Objects:** People, Companies, Deals, Tasks, Notes, Lists
- **Operations:** Full CRUD (Create, Read, Update, Delete)

### Performance Requirements
- **API Response Time:** < 3 seconds for typical queries
- **MCP Response Time:** < 2 seconds for tool calls and responses
- **Reliability:** Handle API rate limits (25 requests/second for webhooks) and temporary failures gracefully
- **Scalability:** Support multiple concurrent Poke connections

## Development Approach

### Core Development Philosophy
**ALWAYS PLAN, SPAR, AND ITERATE BEFORE CODING**
- No single line of code is written until we have a clear plan
- We discuss, brainstorm, and refine every feature before implementation
- Each step is thoroughly planned with the overarching goal in mind

### Implementation Strategy
**MCP-First, Tool-by-Tool Approach**
1. **API Integration First**: Get Attio REST API working with proper authentication (Bearer token)
2. **Read Operations**: Implement search/query tools for People, Companies, and Deals
3. **Write Operations**: Implement tools for adding notes and updating records
4. **Error Handling**: Implement robust error handling, rate limiting, and user feedback
5. **Testing**: Test each tool individually with MCP inspector before Poke integration

### Modular Architecture Principles
**Lego Block Approach - No Interdependencies**
- Each MCP tool is self-contained and independent
- Minimal dependencies between tools
- Easy to add/remove tools without affecting others
- Treat each tool as an independent building block

### Skill Level Considerations
- **Developer Experience:** Beginner to Intermediate
- **Strengths:** 
  - Python basics
  - API integration concepts
  - Following documentation
- **Limitations:**
  - Complex async programming
  - Advanced error handling patterns
  - MCP protocol deep knowledge
- **Approach:** Step-by-step handholding with clear explanations

### AI Assistant Guidelines
- Provide detailed explanations for each step
- Break down complex concepts into simple terms
- Focus on static/simple implementations over dynamic complex ones
- Explain the "why" behind technical decisions
- Offer multiple options when appropriate, with recommendations
- Test and validate each step before moving forward
- **NEVER write code without first planning and discussing the approach**

## Project Structure
```
src/
├── server.py              # Main MCP server with FastMCP
├── tools/
│   ├── __init__.py
│   ├── people.py          # Tools for searching/managing people/contacts
│   ├── companies.py       # Tools for searching/managing companies
│   ├── deals.py           # Tools for managing deals
│   ├── notes.py           # Tools for adding/managing notes
│   └── utils.py           # Helper functions (API requests, error handling)
├── config/
│   └── settings.py        # API keys and configuration
└── tests/
    └── test_tools.py      # Unit tests for MCP tools
```

**Note:** Structure can remain simpler (single file) initially and be modularized later if needed.

## Development Phases

### Phase 1: Planning & Setup ✅
   - ✅ Research Attio REST API documentation
   - ✅ Understand authentication (API Key/Bearer token)
   - ✅ Plan MCP tool structure
   - ✅ Update project instructions
   - Next: Set up API authentication and test connection

### Phase 2: Core Development - Read Operations
   - Implement person/contact search tool
     - Example: "What's the email of Mehdi Ghissassi?"
   - Implement company search tool
   - Implement deal lookup tool
   - Test each tool individually with MCP inspector

### Phase 3: Core Development - Write Operations
   - Implement add note tool
     - Example: "Add call notes from Notion to Attio"
   - Implement record update tool
   - Implement error handling and validation
   - Test write operations thoroughly

### Phase 4: Testing & Refinement
   - Test all tools with MCP inspector
   - Test end-to-end with Poke integration
   - Handle edge cases and errors
   - Optimize performance and response times

### Phase 5: Deployment & Launch
   - Configure environment variables (ATTIO_API_KEY)
   - Deploy to Render
   - Connect to Poke
   - Document usage and examples

### Phase 6: Future Enhancements (Optional)
   - Implement webhook support for real-time updates
   - Add list management tools
   - Add task management tools
   - Implement caching for frequently accessed data

## Success Criteria
- Poke can successfully search for contacts and retrieve their information
- Users can ask "What's the email of [name]?" and get accurate results
- Users can add notes to records through natural language commands
- MCP tools respond within acceptable time limits (< 3 seconds)
- Error handling provides clear, actionable feedback to users
- Integration works reliably with Poke platform
- All CRUD operations function correctly

## Primary Use Cases & Example Workflows

### Use Case 1: Contact Information Lookup
**User Request:** "What's the email of Mehdi Ghissassi?"  
**Flow:**
1. MCP tool searches Attio for person with name matching "Mehdi Ghissassi"
2. Retrieves person record with email attribute
3. Returns formatted response: "Mehdi Ghissassi's email is mehdi@example.com"

**Edge Cases:**
- Multiple matches: Return list of matches with disambiguating info
- No match: Suggest similar names or confirm spelling
- Missing email: "Found Mehdi Ghissassi but no email address on record"

### Use Case 2: Adding Notes to Records
**User Request:** "Add call notes from Notion to Attio for the Acme Corp deal"  
**Flow:**
1. User provides or pastes the notes content
2. MCP tool searches for "Acme Corp" in Companies or Deals
3. Creates a new note associated with that record
4. Confirms success: "Added notes to Acme Corp deal"

**Edge Cases:**
- Record not found: "Couldn't find Acme Corp. Can you provide more details?"
- Permission issues: Clear error about API key permissions

### Use Case 3: Company Information
**User Request:** "Show me details about [Company Name]"  
**Flow:**
1. Search companies by name
2. Retrieve company record with key attributes
3. Format and display relevant information

### Use Case 4: Deal Status Check
**User Request:** "What's the status of the [Deal Name] deal?"  
**Flow:**
1. Search deals by name
2. Retrieve deal status and related information
3. Return formatted status update

### Use Case 5: List Queries
**User Request:** "Show all companies in Austin" or "List my open deals"  
**Flow:**
1. Query relevant list with filters
2. Return formatted list of results
3. Handle pagination if many results

## Communication Style
- Detailed explanations for each concept
- Step-by-step implementation guidance
- Regular check-ins and validation of understanding
- Clear documentation of decisions and rationale

## Notes & Considerations
- **API Rate Limits:** Attio enforces rate limits (25 req/sec for webhooks, TBD for REST API)
- **Authentication:** Secure API key (Bearer token) management for production - store as environment variable
- **Data Privacy:** Handle CRM data securely - no local caching of sensitive information
- **Search Precision:** Implement fuzzy matching for name searches (users may not remember exact spelling)
- **Response Format:** Return data in user-friendly format, not raw API responses
- **Error Messages:** Provide actionable error messages (e.g., "Contact not found. Try searching for similar names?")
- **MCP Protocol:** Ensure full compliance with MCP specifications
- **Modular Design:** Keep tools independent to easily add webhook support later
- **API Key Scopes:** Generate API key with appropriate read/write permissions in Attio dashboard

---

*This document will be updated throughout the project development process to reflect decisions, changes, and progress. The AI assistant will reference this document to maintain appropriate guidance level and technical complexity.*
