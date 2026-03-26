# ============================================================
# MCP Server for PII Protection and Document OCR
# ============================================================
# This server exposes two tools via the Model Context Protocol:
#   1. protect_multi  - Detects and anonymizes PII in text
#   2. mistral_ocr    - Extracts text from documents using Mistral OCR
#
# Run:  python main.py
# URL:  http://localhost:8080/mcp
# ============================================================

from fastmcp import FastMCP
from piiservice import analyze_and_anonymize
from denylist import apply_multiple_deny_lists
from mistral import process_mistral_ocr
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server instance
mcp = FastMCP("presidopii")


# -------------------------------------------------------------
# Tool: protect_multi
# -------------------------------------------------------------
# Detects PII entities in the input text and replaces them
# with anonymized placeholders. Optionally accepts a custom
# deny list to flag additional terms beyond standard PII.
# -------------------------------------------------------------
@mcp.tool()
def protect_multi(text: str, deny_lists: str) -> dict:
    """Analyze and anonymize PII using multiple deny lists.

    Args:
        text: The input text to protect.
        deny_lists: A JSON string of deny lists.
                    e.g. '{"CUSTOM_NAME": ["John", "Alice"]}'
                    Pass '{}' for no deny lists.
    """
    # Parse the JSON string into a Python dict
    deny_dict = json.loads(deny_lists)

    # Run PII detection + anonymization with deny lists
    result = apply_multiple_deny_lists(
        text=text,
        deny_lists=deny_dict
    )

    return {
        "original": text,
        "anonymized": result
    }


# -------------------------------------------------------------
# Tool: mistral_ocr
# -------------------------------------------------------------
# Accepts a base64-encoded file (PDF, image, etc.) and uses
# the Mistral OCR service to extract readable text content.
# Returns the extracted text along with a status indicator.
# -------------------------------------------------------------
@mcp.tool()
def mistral_ocr(file_base64: str, mime_type: str) -> dict:
    """Extract text from documents using Mistral OCR.

    Args:
        file_base64: Base64 encoded file content.
        mime_type: File MIME type (e.g. application/pdf, image/png).
    """
    # Call the Mistral OCR processing function
    result = process_mistral_ocr(
        file_base64=file_base64,
        mime_type=mime_type
    )

    # Return status based on whether an error occurred
    return {
        "status": "success" if "error" not in result else "failed",
        "data": result
    }


# -------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------
# Starts the MCP server using streamable-http transport.
# Accessible at http://localhost:8080/mcp
# -------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ["PORT"]),  # Azure-provided port
        path="/mcp",
        log_level="info"
    )
