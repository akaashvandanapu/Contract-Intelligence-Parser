#!/usr/bin/env python3
"""
Test script to analyze the sample contract extraction
"""

import sys
import os
sys.path.append('.')

from app.enhanced_parser import EnhancedContractParser
import asyncio

async def test_sample_contract():
    """Test extraction with sample contract"""
    parser = EnhancedContractParser()
    
    try:
        result = await parser.parse_contract('sample_contract.pdf')
        print('=== COMPLETE EXTRACTION RESULT ===')
        
        # Check parties
        if result.parties:
            print(f'\nParties found: {len(result.parties)}')
            for i, party in enumerate(result.parties):
                print(f'Party {i+1}: {party.name} - {party.role}')
                print(f'  Email: {party.email}')
                print(f'  Phone: {party.phone}')
                print(f'  Address: {party.address}')
        else:
            print('No parties extracted')
        
        # Check financial details
        if result.financial_details:
            print(f'\nFinancial Details:')
            print(f'  Total Value: {result.financial_details.total_contract_value}')
            print(f'  Currency: {result.financial_details.currency}')
            if result.financial_details.line_items:
                print(f'  Line Items: {len(result.financial_details.line_items)}')
                for item in result.financial_details.line_items[:3]:
                    if hasattr(item, 'description'):
                        desc = item.description
                        price = item.total_price if hasattr(item, 'total_price') else 0
                    else:
                        desc = item.get('description', 'N/A') if isinstance(item, dict) else 'N/A'
                        price = item.get('total_price', 0) if isinstance(item, dict) else 0
                    print(f'    - {desc}: ${price}')
        
        # Check payment terms
        if result.payment_terms:
            print(f'\nPayment Terms:')
            if hasattr(result.payment_terms, 'payment_terms'):
                print(f'  Terms: {result.payment_terms.payment_terms}')
            else:
                print(f'  Terms: {result.payment_terms.get("payment_terms", "N/A") if isinstance(result.payment_terms, dict) else "N/A"}')
            
            if hasattr(result.payment_terms, 'payment_schedule'):
                print(f'  Schedule: {result.payment_terms.payment_schedule}')
            else:
                print(f'  Schedule: {result.payment_terms.get("payment_schedule", "N/A") if isinstance(result.payment_terms, dict) else "N/A"}')
        
        # Check summary
        if result.summary:
            print(f'\nContract Summary:')
            print(f'  Overview: {result.summary.overview}')
            print(f'  Parties: {result.summary.parties_involved}')
            print(f'  Duration: {result.summary.contract_duration}')
            print(f'  Financial: {result.summary.financial_summary}')
        
        # Check confidence scores
        if result.confidence_scores:
            print(f'\nConfidence Scores:')
            for key, value in result.confidence_scores.items():
                print(f'  {key}: {value}')
        
        # Check extracted text
        print(f'\nExtracted Text Length: {len(result.extracted_text) if result.extracted_text else 0}')
        if result.extracted_text:
            print(f'First 500 chars: {result.extracted_text[:500]}')
                
    except Exception as e:
        print(f'Error in complete extraction: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sample_contract())
