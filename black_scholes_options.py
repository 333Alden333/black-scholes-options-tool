import numpy as np
import math
from scipy.stats import norm
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

@dataclass
class OptionContract:
    underlying_symbol: str
    strike_price: float
    expiration_date: datetime
    option_type: OptionType
    current_price: Optional[float] = None
    implied_volatility: Optional[float] = None

@dataclass
class MarketData:
    underlying_price: float
    risk_free_rate: float
    dividend_yield: float = 0.0
    timestamp: datetime = None

@dataclass
class BlackScholesResult:
    theoretical_price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: Optional[float] = None

@dataclass
class TradingSignal:
    action: str
    confidence: float
    reasoning: str
    fair_value: float
    market_price: float
    edge: float

class BlackScholesCalculator:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def time_to_expiration(self, expiration_date: datetime, current_date: datetime = None) -> float:
        """Calculate time to expiration in years"""
        if current_date is None:
            current_date = datetime.now()
        
        time_diff = expiration_date - current_date
        return max(time_diff.total_seconds() / (365.25 * 24 * 3600), 0.0)
    
    def black_scholes_price(self, 
                          spot_price: float,
                          strike_price: float,
                          time_to_expiry: float,
                          risk_free_rate: float,
                          volatility: float,
                          option_type: OptionType,
                          dividend_yield: float = 0.0) -> float:
        """
        Calculate Black-Scholes option price
        
        Args:
            spot_price: Current price of underlying asset
            strike_price: Option strike price
            time_to_expiry: Time to expiration in years
            risk_free_rate: Risk-free interest rate (annualized)
            volatility: Implied volatility (annualized)
            option_type: Call or Put
            dividend_yield: Dividend yield (annualized)
        
        Returns:
            Theoretical option price
        """
        if time_to_expiry <= 0:
            if option_type == OptionType.CALL:
                return max(spot_price - strike_price, 0)
            else:
                return max(strike_price - spot_price, 0)
        
        # Adjust spot price for dividends
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        if option_type == OptionType.CALL:
            price = (adjusted_spot * norm.cdf(d1) - 
                    strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:  # PUT
            price = (strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - 
                    adjusted_spot * norm.cdf(-d1))
        
        return price
    
    def calculate_delta(self,
                       spot_price: float,
                       strike_price: float,
                       time_to_expiry: float,
                       risk_free_rate: float,
                       volatility: float,
                       option_type: OptionType,
                       dividend_yield: float = 0.0) -> float:
        """Calculate option delta (price sensitivity to underlying price change)"""
        if time_to_expiry <= 0:
            if option_type == OptionType.CALL:
                return 1.0 if spot_price > strike_price else 0.0
            else:
                return -1.0 if spot_price < strike_price else 0.0
        
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        
        if option_type == OptionType.CALL:
            return math.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1)
        else:
            return -math.exp(-dividend_yield * time_to_expiry) * norm.cdf(-d1)
    
    def calculate_gamma(self,
                       spot_price: float,
                       strike_price: float,
                       time_to_expiry: float,
                       risk_free_rate: float,
                       volatility: float,
                       dividend_yield: float = 0.0) -> float:
        """Calculate option gamma (delta sensitivity to underlying price change)"""
        if time_to_expiry <= 0:
            return 0.0
        
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        
        return (math.exp(-dividend_yield * time_to_expiry) * norm.pdf(d1)) / (spot_price * volatility * math.sqrt(time_to_expiry))
    
    def calculate_theta(self,
                       spot_price: float,
                       strike_price: float,
                       time_to_expiry: float,
                       risk_free_rate: float,
                       volatility: float,
                       option_type: OptionType,
                       dividend_yield: float = 0.0) -> float:
        """Calculate option theta (time decay)"""
        if time_to_expiry <= 0:
            return 0.0
        
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        if option_type == OptionType.CALL:
            theta = ((-adjusted_spot * norm.pdf(d1) * volatility) / (2 * math.sqrt(time_to_expiry)) +
                    dividend_yield * adjusted_spot * norm.cdf(d1) -
                    risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:
            theta = ((-adjusted_spot * norm.pdf(d1) * volatility) / (2 * math.sqrt(time_to_expiry)) -
                    dividend_yield * adjusted_spot * norm.cdf(-d1) +
                    risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2))
        
        return theta / 365.25  # Convert to daily theta
    
    def calculate_vega(self,
                      spot_price: float,
                      strike_price: float,
                      time_to_expiry: float,
                      risk_free_rate: float,
                      volatility: float,
                      dividend_yield: float = 0.0) -> float:
        """Calculate option vega (volatility sensitivity)"""
        if time_to_expiry <= 0:
            return 0.0
        
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        
        return adjusted_spot * norm.pdf(d1) * math.sqrt(time_to_expiry) / 100  # Convert to 1% vol change
    
    def calculate_rho(self,
                     spot_price: float,
                     strike_price: float,
                     time_to_expiry: float,
                     risk_free_rate: float,
                     volatility: float,
                     option_type: OptionType,
                     dividend_yield: float = 0.0) -> float:
        """Calculate option rho (interest rate sensitivity)"""
        if time_to_expiry <= 0:
            return 0.0
        
        adjusted_spot = spot_price * math.exp(-dividend_yield * time_to_expiry)
        d1 = (math.log(adjusted_spot / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        if option_type == OptionType.CALL:
            rho = strike_price * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
        else:
            rho = -strike_price * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)
        
        return rho / 100  # Convert to 1% rate change
    
    def calculate_implied_volatility(self,
                                   option_price: float,
                                   spot_price: float,
                                   strike_price: float,
                                   time_to_expiry: float,
                                   risk_free_rate: float,
                                   option_type: OptionType,
                                   dividend_yield: float = 0.0,
                                   max_iterations: int = 100,
                                   tolerance: float = 1e-6) -> Optional[float]:
        """Calculate implied volatility using Newton-Raphson method"""
        if time_to_expiry <= 0:
            return None
        
        # Initial guess
        volatility = 0.3
        
        for i in range(max_iterations):
            price = self.black_scholes_price(spot_price, strike_price, time_to_expiry,
                                           risk_free_rate, volatility, option_type, dividend_yield)
            vega = self.calculate_vega(spot_price, strike_price, time_to_expiry,
                                     risk_free_rate, volatility, dividend_yield) * 100
            
            price_diff = price - option_price
            
            if abs(price_diff) < tolerance:
                return volatility
            
            if vega == 0:
                break
            
            volatility -= price_diff / vega
            
            # Keep volatility within reasonable bounds
            volatility = max(0.001, min(volatility, 5.0))
        
        return None
    
    def analyze_option(self,
                      contract: OptionContract,
                      market_data: MarketData,
                      volatility: Optional[float] = None) -> BlackScholesResult:
        """Complete Black-Scholes analysis for an option contract"""
        time_to_expiry = self.time_to_expiration(contract.expiration_date, market_data.timestamp)
        
        # Use provided volatility or calculate from market price
        if volatility is None and contract.current_price is not None:
            volatility = self.calculate_implied_volatility(
                contract.current_price,
                market_data.underlying_price,
                contract.strike_price,
                time_to_expiry,
                market_data.risk_free_rate,
                contract.option_type,
                market_data.dividend_yield
            )
        elif volatility is None and contract.implied_volatility is not None:
            volatility = contract.implied_volatility
        elif volatility is None:
            volatility = 0.3  # Default 30% volatility
        
        if volatility is None:
            raise ValueError("Cannot determine volatility for option analysis")
        
        # Calculate theoretical price and Greeks
        theoretical_price = self.black_scholes_price(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            contract.option_type,
            market_data.dividend_yield
        )
        
        delta = self.calculate_delta(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            contract.option_type,
            market_data.dividend_yield
        )
        
        gamma = self.calculate_gamma(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            market_data.dividend_yield
        )
        
        theta = self.calculate_theta(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            contract.option_type,
            market_data.dividend_yield
        )
        
        vega = self.calculate_vega(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            market_data.dividend_yield
        )
        
        rho = self.calculate_rho(
            market_data.underlying_price,
            contract.strike_price,
            time_to_expiry,
            market_data.risk_free_rate,
            volatility,
            contract.option_type,
            market_data.dividend_yield
        )
        
        return BlackScholesResult(
            theoretical_price=theoretical_price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            implied_volatility=volatility
        )

class OptionsTradingConfirmation:
    def __init__(self, edge_threshold: float = 0.10, min_time_to_expiry: float = 0.02):
        """
        Initialize trading confirmation system
        
        Args:
            edge_threshold: Minimum edge required for trade recommendation (10% default)
            min_time_to_expiry: Minimum time to expiry in years (~1 week default)
        """
        self.calculator = BlackScholesCalculator()
        self.edge_threshold = edge_threshold
        self.min_time_to_expiry = min_time_to_expiry
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_trade_opportunity(self,
                                contract: OptionContract,
                                market_data: MarketData,
                                volatility_estimate: Optional[float] = None) -> TradingSignal:
        """
        Analyze an option trade opportunity and provide confirmation signal
        
        Returns:
            TradingSignal with recommendation and reasoning
        """
        if contract.current_price is None:
            return TradingSignal(
                action="HOLD",
                confidence=0.0,
                reasoning="No market price available for analysis",
                fair_value=0.0,
                market_price=0.0,
                edge=0.0
            )
        
        # Perform Black-Scholes analysis
        try:
            bs_result = self.calculator.analyze_option(contract, market_data, volatility_estimate)
        except Exception as e:
            return TradingSignal(
                action="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                fair_value=0.0,
                market_price=contract.current_price,
                edge=0.0
            )
        
        fair_value = bs_result.theoretical_price
        market_price = contract.current_price
        edge = (fair_value - market_price) / market_price if market_price > 0 else 0
        
        # Check time to expiry
        time_to_expiry = self.calculator.time_to_expiration(contract.expiration_date, market_data.timestamp)
        if time_to_expiry < self.min_time_to_expiry:
            return TradingSignal(
                action="AVOID",
                confidence=0.8,
                reasoning=f"Option expires too soon ({time_to_expiry:.3f} years remaining)",
                fair_value=fair_value,
                market_price=market_price,
                edge=edge
            )
        
        # Generate trading signal based on edge
        confidence = min(abs(edge) / self.edge_threshold, 1.0)
        
        if edge > self.edge_threshold:
            action = "BUY"
            reasoning = f"Option undervalued by {edge:.1%}. Fair value: ${fair_value:.2f} vs Market: ${market_price:.2f}"
        elif edge < -self.edge_threshold:
            action = "SELL"
            reasoning = f"Option overvalued by {abs(edge):.1%}. Fair value: ${fair_value:.2f} vs Market: ${market_price:.2f}"
        else:
            action = "HOLD"
            reasoning = f"Option fairly valued (edge: {edge:.1%}). Fair value: ${fair_value:.2f} vs Market: ${market_price:.2f}"
            confidence = 1.0 - confidence  # Lower confidence for hold signals
        
        # Add Greeks analysis to reasoning
        reasoning += f"\nGreeks - Delta: {bs_result.delta:.3f}, Theta: {bs_result.theta:.2f}, Vega: {bs_result.vega:.2f}"
        
        return TradingSignal(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            fair_value=fair_value,
            market_price=market_price,
            edge=edge
        )
    
    def get_risk_metrics(self,
                        contract: OptionContract,
                        market_data: MarketData,
                        portfolio_exposure: float = 0.0) -> Dict[str, float]:
        """Calculate risk metrics for position sizing"""
        bs_result = self.calculator.analyze_option(contract, market_data)
        
        return {
            'delta_exposure': bs_result.delta * portfolio_exposure,
            'gamma_risk': bs_result.gamma * portfolio_exposure,
            'theta_decay': bs_result.theta * portfolio_exposure,
            'vega_risk': bs_result.vega * portfolio_exposure,
            'max_loss': contract.current_price if contract.current_price else 0.0,
            'time_to_expiry': self.calculator.time_to_expiration(contract.expiration_date, market_data.timestamp)
        }

def example_usage():
    """Example usage of the Black-Scholes options trading tool"""
    
    # Create option contract
    contract = OptionContract(
        underlying_symbol="AAPL",
        strike_price=150.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_price=5.50
    )
    
    # Market data
    market_data = MarketData(
        underlying_price=155.0,
        risk_free_rate=0.05,
        dividend_yield=0.02,
        timestamp=datetime.now()
    )
    
    # Initialize trading confirmation system
    trading_system = OptionsTradingConfirmation(edge_threshold=0.15)
    
    # Analyze trade opportunity
    signal = trading_system.analyze_trade_opportunity(contract, market_data, volatility_estimate=0.25)
    
    print(f"Trading Signal: {signal.action}")
    print(f"Confidence: {signal.confidence:.1%}")
    print(f"Edge: {signal.edge:.1%}")
    print(f"Reasoning: {signal.reasoning}")
    
    # Get risk metrics
    risk_metrics = trading_system.get_risk_metrics(contract, market_data, portfolio_exposure=1000)
    print(f"\nRisk Metrics:")
    for metric, value in risk_metrics.items():
        print(f"{metric}: {value:.4f}")

if __name__ == "__main__":
    example_usage()