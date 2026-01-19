"""
Example usage of the Agentic Invoice Processing System
Demonstrates programmatic usage without the UI.
"""

import os
from dotenv import load_dotenv
from orchestrator import InvoiceProcessingOrchestrator
import json

load_dotenv()


def main():
    """Example of processing an invoice programmatically."""
    
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        print("Get your free API key from: https://openrouter.ai")
        return
    
    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = InvoiceProcessingOrchestrator(openrouter_api_key=api_key)
    
    # Example: Process an invoice
    # Replace with your invoice file path
    invoice_path = "images/IMG_2950.png"  # Example path
    
    if not os.path.exists(invoice_path):
        print(f"Error: Invoice file not found at {invoice_path}")
        print("Please provide a valid invoice file path")
        return
    
    print(f"\nProcessing invoice: {invoice_path}")
    print("=" * 60)
    
    # Process invoice
    results = orchestrator.process_invoice(invoice_path)
    
    # Display results
    print("\n📊 Pipeline Results:")
    print("=" * 60)
    
    # Overall status
    overall_status = results.get("overall_status", "unknown")
    print(f"\nOverall Status: {overall_status.upper()}")
    
    # Display each step
    steps = results.get("steps", {})
    
    # Step 1: Document Ingestion
    if "document_ingestion" in steps:
        step = steps["document_ingestion"]
        print(f"\n1️⃣ Document Ingestion Agent")
        print(f"   Status: {step.get('status', 'unknown')}")
        output = step.get("output", {})
        print(f"   Document ID: {output.get('document_id', 'N/A')}")
        print(f"   Source Type: {output.get('source_type', 'N/A')}")
        raw_text = output.get("raw_text", "")
        print(f"   Raw Text Length: {len(raw_text)} characters")
        if len(raw_text) > 0:
            print(f"   Preview: {raw_text[:100]}...")
    
    # Step 2: Extraction
    if "extraction" in steps:
        step = steps["extraction"]
        print(f"\n2️⃣ Information Extraction Agent")
        print(f"   Status: {step.get('status', 'unknown')}")
        output = step.get("output", {})
        print(f"   Extracted Fields:")
        print(f"     - Biller Name: {output.get('biller_name', 'N/A')}")
        print(f"     - Biller Address: {output.get('biller_address', 'N/A')}")
        print(f"     - Total Amount: {output.get('total_amount', 'N/A')}")
        print(f"     - Due Date: {output.get('due_date', 'N/A')}")
    
    # Step 3: Validation
    if "validation" in steps:
        step = steps["validation"]
        print(f"\n3️⃣ Validation Agent")
        print(f"   Status: {step.get('status', 'unknown')}")
        output = step.get("output", {})
        print(f"   Validation Status: {output.get('status', 'N/A')}")
        errors = output.get("errors", [])
        if errors:
            print(f"   Errors: {', '.join(errors)}")
        else:
            print(f"   ✅ All validations passed!")
    
    # Step 4: Tool Decision
    if "tool_decision" in steps:
        step = steps["tool_decision"]
        print(f"\n4️⃣ Tool Decision Agent")
        print(f"   Status: {step.get('status', 'unknown')}")
        output = step.get("output", {})
        print(f"   Should Write to DB: {output.get('should_write', False)}")
        print(f"   Reason: {output.get('reason', 'N/A')}")
    
    # Step 5: Database Write
    if "database_write" in steps:
        step = steps["database_write"]
        print(f"\n5️⃣ Database Tool")
        print(f"   Status: {step.get('status', 'unknown')}")
        if step.get("status") == "skipped":
            print(f"   Reason: {step.get('reason', 'N/A')}")
        else:
            output = step.get("output", {})
            if output.get("success"):
                print(f"   ✅ Invoice written successfully!")
                print(f"   Invoice ID: {output.get('invoice_id', 'N/A')}")
            else:
                print(f"   ❌ Error: {output.get('message', 'N/A')}")
    
    # Save full results to JSON
    output_file = "example_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("Processing complete!")


if __name__ == "__main__":
    main()
