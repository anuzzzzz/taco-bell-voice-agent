#!/usr/bin/env python3
"""
Quick demo script for showcasing the Taco Bell Voice Agent
"""

import sys
import os
from colorama import init, Fore
from main import TacoBellVoiceAgent

init(autoreset=True)

def run_demo():
    """Run a quick demo of the system"""
    
    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}🌮 TACO BELL VOICE AGENT - DEMO")
    print(f"{Fore.MAGENTA}{'='*70}\n")
    
    print(f"{Fore.YELLOW}This demo will showcase:")
    print(f"  • Natural conversation flow")
    print(f"  • Order taking and modifications")
    print(f"  • Menu knowledge (RAG)")
    print(f"  • Error handling")
    print(f"  • Brand voice\n")
    
    input(f"{Fore.GREEN}Press Enter to start demo...")
    
    # Initialize agent in text mode
    agent = TacoBellVoiceAgent(
        enable_voice=False,
        enable_logging=True,
        log_dir="logs/demo"
    )
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Simple Order",
            "conversation": [
                "Hi",
                "I want two crunchy tacos",
                "That's all",
                "Yes"
            ]
        },
        {
            "name": "Order with Modifications",
            "conversation": [
                "Hello",
                "Give me three soft tacos",
                "No lettuce on those",
                "And a large Baja Blast",
                "That's everything",
                "Correct"
            ]
        },
        {
            "name": "Menu Query",
            "conversation": [
                "Hi",
                "What's your cheapest burrito?",
                "I'll take that",
                "And do you have vegetarian options?",
                "Add cinnamon twists too",
                "That's all",
                "Yes"
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}SCENARIO {i}: {scenario['name']}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        agent.conversation.reset()
        agent.greet_customer()
        
        for user_input in scenario['conversation']:
            print(f"{Fore.CYAN}👤 Customer: {user_input}")
            response, state = agent.process_customer_input(user_input, 1.0)
            print(f"{Fore.GREEN}🤖 Agent: {response}")
            print(f"{Fore.WHITE}[State: {state.value}]\n")
            
            input(f"{Fore.YELLOW}Press Enter to continue...")
        
        # Show final order
        if agent.conversation.order.items:
            print(f"\n{Fore.GREEN}Final Order:")
            print(agent.conversation.order.get_summary())
    
    # Show statistics
    print(f"\n{Fore.MAGENTA}{'='*70}")
    agent.print_statistics()
    
    print(f"\n{Fore.GREEN}Demo complete! Logs saved to logs/demo/")

if __name__ == "__main__":
    run_demo()