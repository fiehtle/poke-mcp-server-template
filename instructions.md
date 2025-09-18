# Poke-BFL Project Instructions

## Project Overview
**Project Name:** Poke-BFL (Poke + Black Forest Labs + FLUX)  
**Purpose:** Create an MCP integration that allows Poke AI assistant to generate images using Black Forest Labs' FLUX model via Fal.ai API  
**Type:** MCP Server Integration  
**Context:** This project is part of the Poke MCP Challenge from HackMIT, involving the creation of custom automations and MCP integrations using The Interaction Company's Poke platform.

## Project Goals
- Enable Poke to generate high-quality images on demand using FLUX model
- Provide a seamless integration between Poke and Fal.ai's FLUX API
- Create reusable MCP tools for image generation with various parameters
- Allow users to ask Poke to create images through natural language

## Target Audience
- Poke AI assistant users who want image generation capabilities
- Developers who want to integrate FLUX image generation into their workflows
- Anyone participating in the Poke MCP Challenge

## Core Features
- **Image Generation Tool:** Generate images from text prompts using FLUX model
- **Parameter Control:** Allow customization of image generation parameters (size, style, etc.)
- **Error Handling:** Robust error handling and user-friendly error messages
- **API Integration:** Seamless connection to Fal.ai's FLUX API
- **MCP Protocol:** Full MCP compliance for Poke integration

## Technical Requirements
### Technology Stack
- **MCP Server:** Python with FastMCP framework
- **API Integration:** Fal.ai FLUX API
- **Deployment:** Render (streamable HTTP transport)
- **Protocol:** MCP (Model Context Protocol)

### Performance Requirements
- **API Response Time:** < 30 seconds for image generation (typical for FLUX)
- **MCP Response Time:** < 2 seconds for tool calls and responses
- **Reliability:** Handle API rate limits and temporary failures gracefully
- **Scalability:** Support multiple concurrent Poke connections

## Development Approach

### Core Development Philosophy
**ALWAYS PLAN, SPAR, AND ITERATE BEFORE CODING**
- No single line of code is written until we have a clear plan
- We discuss, brainstorm, and refine every feature before implementation
- Each step is thoroughly planned with the overarching goal in mind

### Implementation Strategy
**MCP-First, Tool-by-Tool Approach**
1. **API Integration First**: Get Fal.ai FLUX API working with proper authentication
2. **MCP Tool Development**: Create individual MCP tools for different image generation features
3. **Error Handling**: Implement robust error handling and user feedback
4. **Testing**: Test each tool individually with MCP inspector before Poke integration

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
│   ├── image_generation.py  # FLUX image generation tool
│   └── utils.py            # Helper functions
├── config/
│   └── settings.py         # API keys and configuration
└── tests/
    └── test_tools.py       # Unit tests for MCP tools
```

## Development Phases
1. **Phase 1:** Planning & Setup
   - Research Fal.ai FLUX API documentation
   - Set up API authentication
   - Plan MCP tool structure
2. **Phase 2:** Core Development
   - Implement basic image generation tool
   - Add parameter customization
   - Implement error handling
3. **Phase 3:** Testing & Refinement
   - Test with MCP inspector
   - Test with Poke integration
   - Optimize performance
4. **Phase 4:** Deployment & Launch
   - Deploy to Render
   - Connect to Poke
   - Document usage

## Success Criteria
- Poke can successfully generate images when asked
- MCP tools respond within acceptable time limits
- Error handling provides clear feedback to users
- Integration works reliably with Poke platform

## Communication Style
- Detailed explanations for each concept
- Step-by-step implementation guidance
- Regular check-ins and validation of understanding
- Clear documentation of decisions and rationale

## Notes & Considerations
- **API Rate Limits:** Fal.ai may have rate limits we need to handle
- **Image Storage:** Consider where generated images will be stored/accessed
- **Authentication:** Secure API key management for production
- **MCP Protocol:** Ensure full compliance with MCP specifications

---

*This document will be updated throughout the project development process to reflect decisions, changes, and progress. The AI assistant will reference this document to maintain appropriate guidance level and technical complexity.*
