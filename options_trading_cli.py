#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add the current directory to Python path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from black_scholes_options import (
    OptionContract, MarketData, OptionType, 
    BlackScholesCalculator, OptionsTradingConfirmation
)

def parse_date(date_string: str) -> datetime:
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD or MM/DD/YYYY")

def parse_option_type(option_type_str: str) -> OptionType:
    """Parse option type string"""
    option_type_str = option_type_str.lower()
    if option_type_str in ['call', 'c']:
        return OptionType.CALL
    elif option_type_str in ['put', 'p']:
        return OptionType.PUT
    else:
        raise ValueError(f"Invalid option type: {option_type_str}. Use 'call' or 'put'")

def format_results(bs_result, signal=None):
    """Format and display results"""
    print("\n" + "="*60)
    print("BLACK-SCHOLES ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nTHEORETICAL PRICING:")
    print(f"  Fair Value:          ${bs_result.theoretical_price:.2f}")
    if bs_result.implied_volatility:
        print(f"  Implied Volatility:  {bs_result.implied_volatility:.1%}")
    
    print(f"\nTHE GREEKS:")
    print(f"  Delta (Δ):           {bs_result.delta:.4f}")
    print(f"  Gamma (Γ):           {bs_result.gamma:.4f}")
    print(f"  Theta (Θ):           ${bs_result.theta:.2f}/day")
    print(f"  Vega (ν):            ${bs_result.vega:.2f}/1% vol")
    print(f"  Rho (ρ):             ${bs_result.rho:.2f}/1% rate")
    
    if signal:
        print(f"\nTRADING RECOMMENDATION:")
        print(f"  Action:              {signal.action}")
        print(f"  Confidence:          {signal.confidence:.1%}")
        print(f"  Edge:                {signal.edge:.1%}")
        print(f"  Market Price:        ${signal.market_price:.2f}")
        print(f"  Fair Value:          ${signal.fair_value:.2f}")
        print(f"\n  Analysis:")
        for line in signal.reasoning.split('\n'):
            print(f"    {line}")
    
    print("\n" + "="*60)

def interactive_mode():
    """Interactive mode for entering option data"""
    print("\n" + "="*60)
    print("INTERACTIVE BLACK-SCHOLES OPTIONS ANALYZER")
    print("="*60)
    
    try:
        # Get option contract details
        print("\nOPTION CONTRACT DETAILS:")
        symbol = input("Underlying symbol (e.g., AAPL): ").strip().upper()
        
        while True:
            try:
                strike = float(input("Strike price: $"))
                break
            except ValueError:
                print("Please enter a valid number for strike price")
        
        while True:
            try:
                exp_date_str = input("Expiration date (YYYY-MM-DD): ").strip()
                expiration_date = parse_date(exp_date_str)
                break
            except ValueError as e:
                print(f"Error: {e}")
        
        while True:
            try:
                option_type_str = input("Option type (call/put): ").strip()
                option_type = parse_option_type(option_type_str)
                break
            except ValueError as e:
                print(f"Error: {e}")
        
        current_price = None
        price_input = input("Current option price (optional, press Enter to skip): $").strip()
        if price_input:
            try:
                current_price = float(price_input)
            except ValueError:
                print("Invalid price format, continuing without market price")
        
        # Get market data
        print("\nMARKET DATA:")
        while True:
            try:
                underlying_price = float(input("Current underlying price: $"))
                break
            except ValueError:
                print("Please enter a valid number for underlying price")
        
        while True:
            try:
                risk_free_rate = float(input("Risk-free rate (e.g., 0.05 for 5%): "))
                break
            except ValueError:
                print("Please enter a valid number for risk-free rate")
        
        dividend_yield = 0.0
        div_input = input("Dividend yield (optional, press Enter for 0): ").strip()
        if div_input:
            try:
                dividend_yield = float(div_input)
            except ValueError:
                print("Invalid dividend yield format, using 0")
        
        volatility = None
        vol_input = input("Volatility estimate (optional, e.g., 0.25 for 25%): ").strip()
        if vol_input:
            try:
                volatility = float(vol_input)
            except ValueError:
                print("Invalid volatility format, will calculate from market price if available")
        
        # Create objects and analyze
        contract = OptionContract(
            underlying_symbol=symbol,
            strike_price=strike,
            expiration_date=expiration_date,
            option_type=option_type,
            current_price=current_price
        )
        
        market_data = MarketData(
            underlying_price=underlying_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            timestamp=datetime.now()
        )
        
        # Perform analysis
        calculator = BlackScholesCalculator()
        bs_result = calculator.analyze_option(contract, market_data, volatility)
        
        signal = None
        if current_price is not None:
            trading_system = OptionsTradingConfirmation()
            signal = trading_system.analyze_trade_opportunity(contract, market_data, volatility)
        
        format_results(bs_result, signal)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Black-Scholes Options Trading Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python options_trading_cli.py --interactive
  
  # Analyze a specific option
  python options_trading_cli.py --symbol AAPL --strike 150 --expiry 2024-01-20 \\
    --type call --underlying-price 155 --risk-free-rate 0.05 --current-price 5.50
  
  # Calculate fair value only
  python options_trading_cli.py --symbol TSLA --strike 200 --expiry 2024-02-15 \\
    --type put --underlying-price 195 --risk-free-rate 0.05 --volatility 0.40
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    
    # Option contract parameters
    parser.add_argument('--symbol', type=str,
                       help='Underlying symbol (e.g., AAPL)')
    parser.add_argument('--strike', type=float,
                       help='Strike price')
    parser.add_argument('--expiry', type=str,
                       help='Expiration date (YYYY-MM-DD)')
    parser.add_argument('--type', choices=['call', 'put', 'c', 'p'],
                       help='Option type (call or put)')
    parser.add_argument('--current-price', type=float,
                       help='Current option market price')
    
    # Market data parameters
    parser.add_argument('--underlying-price', type=float,
                       help='Current underlying asset price')
    parser.add_argument('--risk-free-rate', type=float,
                       help='Risk-free interest rate (decimal, e.g., 0.05 for 5%%)')
    parser.add_argument('--dividend-yield', type=float, default=0.0,
                       help='Dividend yield (decimal, default: 0.0)')
    parser.add_argument('--volatility', type=float,
                       help='Volatility estimate (decimal, e.g., 0.25 for 25%%)')
    
    # Analysis parameters
    parser.add_argument('--edge-threshold', type=float, default=0.10,
                       help='Edge threshold for trading signals (default: 0.10)')
    parser.add_argument('--output-format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    # Validate required arguments for non-interactive mode
    required_args = ['symbol', 'strike', 'expiry', 'type', 'underlying_price', 'risk_free_rate']
    missing_args = [arg for arg in required_args if getattr(args, arg.replace('-', '_')) is None]
    
    if missing_args:
        print(f"Error: Missing required arguments: {', '.join(['--' + arg for arg in missing_args])}")
        print("Use --interactive for interactive mode or --help for usage information.")
        sys.exit(1)
    
    try:
        # Parse and create objects
        expiration_date = parse_date(args.expiry)
        option_type = parse_option_type(args.type)
        
        contract = OptionContract(
            underlying_symbol=args.symbol.upper(),
            strike_price=args.strike,
            expiration_date=expiration_date,
            option_type=option_type,
            current_price=args.current_price
        )
        
        market_data = MarketData(
            underlying_price=args.underlying_price,
            risk_free_rate=args.risk_free_rate,
            dividend_yield=args.dividend_yield,
            timestamp=datetime.now()
        )
        
        # Perform analysis
        calculator = BlackScholesCalculator()
        bs_result = calculator.analyze_option(contract, market_data, args.volatility)
        
        signal = None
        if args.current_price is not None:
            trading_system = OptionsTradingConfirmation(edge_threshold=args.edge_threshold)
            signal = trading_system.analyze_trade_opportunity(contract, market_data, args.volatility)
        
        # Output results
        if args.output_format == 'json':
            result = {
                'theoretical_price': bs_result.theoretical_price,
                'greeks': {
                    'delta': bs_result.delta,
                    'gamma': bs_result.gamma,
                    'theta': bs_result.theta,
                    'vega': bs_result.vega,
                    'rho': bs_result.rho
                },
                'implied_volatility': bs_result.implied_volatility
            }
            
            if signal:
                result['trading_signal'] = {
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'edge': signal.edge,
                    'reasoning': signal.reasoning
                }
            
            print(json.dumps(result, indent=2))
        else:
            format_results(bs_result, signal)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()