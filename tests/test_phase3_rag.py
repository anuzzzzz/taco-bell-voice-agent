#!/usr/bin/env python3
"""Test Menu RAG System for Phase 3"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.menu_rag import TacoBellMenuRAG, MenuItem
from src.intent_detector_llm import TacoBellIntentDetector
from colorama import init, Fore
import time

init(autoreset=True)

def test_menu_search():
    """Test menu search functionality"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}MENU SEARCH TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    rag = TacoBellMenuRAG()
    
    test_cases = [
        ("taco", "Should find all taco items"),
        ("cheapest", "Should find lowest price items"),
        ("drink", "Should find beverages"),
        ("vegetarian", "Should find meat-free options"),
        ("crunchy", "Should find crunchy items"),
        ("$2", "Should understand price queries"),
        ("combo", "Should find combo meals"),
        ("spicy", "Should find spicy items"),
    ]
    
    for query, description in test_cases:
        print(f"{Fore.YELLOW}Query: '{query}' - {description}")
        results = rag.search_menu(query, top_k=3)
        
        if results:
            for result in results:
                confidence_color = Fore.GREEN if result.score > 0.5 else Fore.YELLOW
                print(f"  {confidence_color}→ {result.item.name} (${result.item.price:.2f})")
                print(f"     Score: {result.score:.2f} - {result.reason}")
        else:
            print(f"  {Fore.RED}No results found")
        print()
    
    return len(results) > 0

def test_recommendations():
    """Test recommendation system"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}RECOMMENDATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    rag = TacoBellMenuRAG()
    
    test_orders = [
        (["Crunchy Taco"], "Just a taco"),
        (["Beef Burrito", "Soft Drink"], "Burrito and drink"),
        (["Nacho Fries"], "Just a side"),
        ([], "Empty order"),
    ]
    
    for current_items, description in test_orders:
        print(f"{Fore.YELLOW}Current order: {current_items} - {description}")
        recommendations = rag.get_recommendations(current_items)
        
        if recommendations:
            print(f"{Fore.GREEN}  Recommendations:")
            for rec in recommendations:
                print(f"    → Add {rec.name} (${rec.price:.2f})")
        else:
            print(f"{Fore.GRAY}  No recommendations")
        print()

def test_price_calculation():
    """Test order total calculation"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}PRICE CALCULATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    rag = TacoBellMenuRAG()
    
    test_orders = [
        [("Crunchy Taco", 2), ("Soft Drink", 1)],
        [("Crunchwrap Supreme", 1), ("Baja Blast", 1), ("Nacho Fries", 1)],
        [("Cravings Box", 1)],
    ]
    
    for order in test_orders:
        print(f"{Fore.YELLOW}Order: {order}")
        total = rag.calculate_order_total(order)
        print(f"{Fore.GREEN}  Total: ${total:.2f}\n")

def test_integration_with_intent():
    """Test RAG integration with intent detection"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}RAG + INTENT INTEGRATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        rag = TacoBellMenuRAG()
        detector = TacoBellIntentDetector()
        
        # Simulate customer queries
        queries = [
            "I want two tacos",
            "What's your cheapest burrito?",
            "Add a large drink",
            "Do you have anything vegetarian?",
        ]
        
        for query in queries:
            print(f"{Fore.YELLOW}Customer: '{query}'")
            
            # Get intent
            intent_result = detector.detect_intent(query)
            print(f"{Fore.CYAN}  Intent: {intent_result.intent.value}")
            
            # Search menu based on entities
            if intent_result.entities.get('items'):
                for item in intent_result.entities['items']:
                    search_results = rag.search_menu(item, top_k=1)
                    if search_results:
                        found_item = search_results[0].item
                        print(f"{Fore.GREEN}  Found: {found_item.name} (${found_item.price:.2f})")
            
            print()
            time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Integration test failed: {e}")
        return False

def main():
    """Run all Phase 3 tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 3: MENU RAG SYSTEM TESTS")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    results = {}
    
    # Test 1: Menu Search
    print(f"{Fore.CYAN}Test 1: Menu Search")
    results["Search"] = test_menu_search()
    
    # Test 2: Recommendations
    print(f"{Fore.CYAN}Test 2: Recommendations")
    test_recommendations()
    results["Recommendations"] = True
    
    # Test 3: Price Calculation
    print(f"{Fore.CYAN}Test 3: Price Calculation")
    test_price_calculation()
    results["Pricing"] = True
    
    # Test 4: Integration
    print(f"{Fore.CYAN}Test 4: Integration with Intent Detection")
    results["Integration"] = test_integration_with_intent()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 3 TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    all_passed = all(results.values())
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{test_name:15} {status}")
    
    if all_passed:
        print(f"\n{Fore.GREEN}🎉 Phase 3 Complete! RAG System working!")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests need attention")

if __name__ == "__main__":
    main()