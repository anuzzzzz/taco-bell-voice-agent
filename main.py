#!/usr/bin/env python3
"""
Taco Bell Voice Agent - Complete Integrated Application
Phase 7: Full system integration with all components
"""

import os
import sys
import time
import json
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Import all our components
from src.voice_pipeline import VoicePipeline
from src.conversation_manager_v2 import EnhancedConversationManager, ConversationState
from src.menu_rag import TacoBellMenuRAG
from src.response_generator import TacoBellResponseGenerator
from src.error_handler import ErrorHandler, ErrorType

init(autoreset=True)
load_dotenv()

class TacoBellVoiceAgent:
    """Complete Taco Bell Drive-Thru Voice Agent"""
    
    def __init__(
        self, 
        whisper_model: str = "base",
        enable_voice: bool = True,
        enable_logging: bool = True,
        log_dir: str = "logs"
    ):
        """
        Initialize the complete voice agent
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium)
            enable_voice: Enable voice I/O (False for text-only testing)
            enable_logging: Enable conversation logging
            log_dir: Directory for logs
        """
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🌮 TACO BELL VOICE AGENT - INITIALIZING")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        self.enable_voice = enable_voice
        self.enable_logging = enable_logging
        self.log_dir = Path(log_dir)
        
        # Create log directory
        if enable_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = self.log_dir / f"session_{self.session_id}.json"
            self.session_log = {
                "session_id": self.session_id,
                "start_time": datetime.now().isoformat(),
                "conversations": []
            }
        else:
            self.log_file = None
            self.session_log = None
        
        # Initialize components
        try:
            # Voice pipeline (optional)
            if enable_voice:
                print(f"{Fore.YELLOW}Initializing voice pipeline...")
                self.voice = VoicePipeline(model_size=whisper_model)
            else:
                print(f"{Fore.YELLOW}Voice disabled - text mode only")
                self.voice = None
            
            # Conversation manager
            print(f"{Fore.YELLOW}Initializing conversation manager...")
            self.conversation = EnhancedConversationManager()
            
            # Menu RAG
            print(f"{Fore.YELLOW}Initializing menu RAG system...")
            self.menu = TacoBellMenuRAG()
            
            # Response generator
            print(f"{Fore.YELLOW}Initializing response generator...")
            self.response_gen = TacoBellResponseGenerator()
            
            print(f"\n{Fore.GREEN}✓ All components initialized successfully!")
            print(f"{Fore.GREEN}{'='*70}\n")
            
            # Performance tracking
            self.stats = {
                "conversations": 0,
                "successful_orders": 0,
                "errors": 0,
                "avg_conversation_length": 0.0,
                "avg_order_value": 0.0
            }
            
        except Exception as e:
            print(f"{Fore.RED}✗ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def greet_customer(self):
        """Greet the customer"""
        greeting = self.response_gen.get_time_based_greeting()
        self._output(greeting)
        return greeting
    
    def _output(self, text: str):
        """Output text (speak or print)"""
        print(f"{Fore.GREEN}🤖 Agent: {text}")
        if self.voice:
            self.voice.speak(text)
    
    def _input(self) -> tuple[str, float]:
        """Get input (voice or text)"""
        if self.voice:
            print(f"{Fore.YELLOW}🎤 Listening...")
            text, confidence = self.voice.process_voice_input()
            return text, confidence
        else:
            # Text mode
            text = input(f"{Fore.CYAN}👤 Customer: ").strip()
            return text, 1.0
    
    def process_customer_input(self, text: str, confidence: float) -> tuple[str, ConversationState]:
        """
        Process customer input through the conversation manager
        
        Returns:
            Tuple of (response, new_state)
        """
        response, state = self.conversation.process_input(text, confidence)
        return response, state
    
    def run_conversation(self) -> Dict:
        """
        Run a complete customer conversation
        
        Returns:
            Dictionary with conversation summary
        """
        print(f"{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}🚗 NEW CUSTOMER")
        print(f"{Fore.MAGENTA}{'='*70}\n")
        
        conversation_start = time.time()
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "turns": [],
            "final_order": None,
            "total": 0.0,
            "success": False
        }
        
        # Reset conversation manager for new customer
        self.conversation.reset()
        
        # Greet customer
        greeting = self.greet_customer()
        conversation_data["turns"].append({
            "agent": greeting,
            "customer": None
        })
        
        # Conversation loop
        turn_count = 0
        max_turns = 20  # Prevent infinite loops
        
        while turn_count < max_turns:
            turn_count += 1
            
            try:
                # Get customer input
                customer_text, confidence = self._input()
                
                if not customer_text:
                    continue
                
                print(f"{Fore.CYAN}👤 Customer: {customer_text}")
                
                # Process input
                response, state = self.process_customer_input(customer_text, confidence)
                
                # Output response
                self._output(response)
                
                # Log turn
                conversation_data["turns"].append({
                    "customer": customer_text,
                    "confidence": confidence,
                    "agent": response,
                    "state": state.value
                })
                
                # Check if conversation is complete
                if state == ConversationState.GOODBYE:
                    conversation_data["success"] = True
                    conversation_data["final_order"] = self._get_order_summary()
                    break
                
                # Check if customer wants to quit
                if customer_text.lower() in ['quit', 'exit', 'cancel', 'never mind']:
                    self._output("No problem! Have a great day!")
                    break
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Conversation interrupted by user")
                break
            except Exception as e:
                print(f"{Fore.RED}Error in conversation: {e}")
                self.stats["errors"] += 1
                self._output("I'm having technical difficulties. Let me start over.")
                break
        
        # End of conversation
        conversation_end = time.time()
        conversation_data["duration"] = conversation_end - conversation_start
        conversation_data["turn_count"] = turn_count
        
        # Update stats
        self.stats["conversations"] += 1
        if conversation_data["success"]:
            self.stats["successful_orders"] += 1
            if conversation_data["final_order"]:
                total = conversation_data["final_order"].get("total", 0.0)
                self.stats["avg_order_value"] = (
                    (self.stats["avg_order_value"] * (self.stats["successful_orders"] - 1) + total) 
                    / self.stats["successful_orders"]
                )
        
        # Log conversation
        if self.enable_logging:
            self.session_log["conversations"].append(conversation_data)
            self._save_log()
        
        # Print summary
        self._print_conversation_summary(conversation_data)
        
        return conversation_data
    
    def _get_order_summary(self) -> Dict:
        """Get current order summary"""
        order = self.conversation.order
        return {
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "modifications": item.modifications
                }
                for item in order.items
            ],
            "total": order.get_total(),
            "item_count": len(order.items)
        }
    
    def _print_conversation_summary(self, data: Dict):
        """Print conversation summary"""
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}📊 CONVERSATION SUMMARY")
        print(f"{Fore.MAGENTA}{'='*70}\n")
        
        print(f"{Fore.CYAN}Duration: {data['duration']:.1f}s")
        print(f"{Fore.CYAN}Turns: {data['turn_count']}")
        print(f"{Fore.CYAN}Success: {data['success']}")
        
        if data.get("final_order") and data["final_order"]["items"]:
            print(f"\n{Fore.GREEN}Final Order:")
            for item in data["final_order"]["items"]:
                mods = f" ({', '.join(item['modifications'])})" if item['modifications'] else ""
                print(f"  • {item['quantity']}x {item['name']}{mods} - ${item['price'] * item['quantity']:.2f}")
            print(f"\n{Fore.GREEN}Total: ${data['final_order']['total']:.2f}")
        else:
            print(f"\n{Fore.YELLOW}No order completed")
        
        print(f"\n{Fore.MAGENTA}{'='*70}\n")
    
    def _save_log(self):
        """Save session log to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.session_log, f, indent=2)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not save log: {e}")
    
    def print_statistics(self):
        """Print session statistics"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📈 SESSION STATISTICS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        print(f"Total Conversations: {self.stats['conversations']}")
        print(f"Successful Orders: {self.stats['successful_orders']}")
        print(f"Success Rate: {self.stats['successful_orders']/max(1, self.stats['conversations'])*100:.1f}%")
        print(f"Errors: {self.stats['errors']}")
        print(f"Avg Order Value: ${self.stats['avg_order_value']:.2f}")
        
        # Get diagnostics from conversation manager
        diagnostics = self.conversation.get_diagnostics()
        print(f"\n{Fore.YELLOW}Error Statistics:")
        if diagnostics.get("error_stats"):
            error_stats = diagnostics["error_stats"]
            print(f"  Total Errors: {error_stats.get('total_errors', 0)}")
            if error_stats.get('by_type'):
                for error_type, count in error_stats['by_type'].items():
                    print(f"  {error_type}: {count}")
        
        print(f"\n{Fore.CYAN}{'='*70}\n")
    
    def run_interactive_mode(self):
        """Run in interactive mode with menu"""
        while True:
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.CYAN}🌮 TACO BELL VOICE AGENT - MAIN MENU")
            print(f"{Fore.CYAN}{'='*70}\n")
            
            print(f"{Fore.YELLOW}1. Start new conversation")
            print(f"{Fore.YELLOW}2. View statistics")
            print(f"{Fore.YELLOW}3. Test menu search")
            print(f"{Fore.YELLOW}4. View diagnostics")
            print(f"{Fore.YELLOW}5. Exit")
            
            choice = input(f"\n{Fore.GREEN}Select option: ").strip()
            
            if choice == "1":
                self.run_conversation()
            elif choice == "2":
                self.print_statistics()
            elif choice == "3":
                self._test_menu_search()
            elif choice == "4":
                self._print_diagnostics()
            elif choice == "5":
                print(f"\n{Fore.GREEN}Goodbye! Session saved to {self.log_file}")
                break
            else:
                print(f"{Fore.RED}Invalid option")
    
    def _test_menu_search(self):
        """Test menu search functionality"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🔍 MENU SEARCH TEST")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        query = input(f"{Fore.YELLOW}Enter search query: ").strip()
        if not query:
            return
        
        results = self.menu.search_menu(query, top_k=5)
        
        if results:
            print(f"\n{Fore.GREEN}Search Results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.item.name} - ${result.item.price:.2f}")
                print(f"   Score: {result.score:.2f} ({result.reason})")
                print(f"   {result.item.description}\n")
        else:
            print(f"{Fore.YELLOW}No results found")
    
    def _print_diagnostics(self):
        """Print system diagnostics"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🔧 SYSTEM DIAGNOSTICS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        diagnostics = self.conversation.get_diagnostics()
        print(json.dumps(diagnostics, indent=2))
        print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Taco Bell Voice Agent")
    parser.add_argument(
        "--text-only", 
        action="store_true", 
        help="Run in text-only mode (no voice I/O)"
    )
    parser.add_argument(
        "--whisper-model", 
        default="base", 
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size"
    )
    parser.add_argument(
        "--no-logging",
        action="store_true",
        help="Disable conversation logging"
    )
    parser.add_argument(
        "--single-conversation",
        action="store_true",
        help="Run single conversation and exit"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.RED}Error: No OPENAI_API_KEY found in .env file")
        print(f"{Fore.YELLOW}Please create a .env file with your OpenAI API key")
        return
    
    try:
        # Initialize agent
        agent = TacoBellVoiceAgent(
            whisper_model=args.whisper_model,
            enable_voice=not args.text_only,
            enable_logging=not args.no_logging
        )
        
        # Run mode
        if args.single_conversation:
            agent.run_conversation()
            agent.print_statistics()
        else:
            agent.run_interactive_mode()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()