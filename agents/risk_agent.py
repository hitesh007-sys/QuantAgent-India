def compute_risk(
    entry_price: float,
    direction: str,
    support: float,
    resistance: float
) -> dict:
    """
    Computes dynamic stop loss and take profit levels based on Support and Resistance.
    """
    if direction == "BUY":
        # Place Stop Loss slightly below support, Take Profit slightly below resistance
        stop_loss   = support * 0.995
        take_profit = resistance * 0.995
        
        # Fallback safeguard: If price broke out of normal bounds, use standard percentages
        if stop_loss >= entry_price: stop_loss = entry_price * 0.98
        if take_profit <= entry_price: take_profit = entry_price * 1.04
            
    else: # SELL
        # Place Stop Loss slightly above resistance, Take Profit slightly above support
        stop_loss   = resistance * 1.005
        take_profit = support * 1.005
        
        # Fallback safeguard
        if stop_loss <= entry_price: stop_loss = entry_price * 1.02
        if take_profit >= entry_price: take_profit = entry_price * 0.96

    # Round the final price targets
    stop_loss = round(stop_loss, 2)
    take_profit = round(take_profit, 2)

    # Calculate exact risk and reward in Rupees
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)

    # Calculate Dynamic Risk/Reward Ratio
    if risk > 0:
        rr_ratio = round(reward / risk, 2)
    else:
        rr_ratio = 1.0
        
    # Dynamically assign Risk Level based on the math
    if rr_ratio >= 2.0:
        risk_level = "Low"     # Great reward for the risk
    elif rr_ratio >= 1.2:
        risk_level = "Medium"  # Standard trade
    else:
        risk_level = "High"    # Poor reward for the risk

    potential_profit = round(reward, 2)
    potential_loss   = round(risk, 2)

    # Format the ratio as a string for the dashboard
    formatted_ratio = f"1:{rr_ratio}"

    return {
        "direction":       direction,
        "entry":           round(entry_price, 2),
        "stop_loss":       stop_loss,
        "take_profit":     take_profit,
        "rr_ratio":        formatted_ratio,
        "risk_level":      risk_level,
        "potential_profit": potential_profit,
        "potential_loss":   potential_loss
    }


def format_risk_summary(risk_data: dict) -> str:
    """Returns plain English risk summary."""
    return f"""
Trade Direction: {risk_data['direction']}
Entry Price: {risk_data['entry']}
Stop Loss: {risk_data['stop_loss']}
Take Profit: {risk_data['take_profit']}
Risk/Reward Ratio: {risk_data['rr_ratio']}
Risk Level: {risk_data['risk_level']}
Potential Profit: {risk_data['potential_profit']}
Potential Loss: {risk_data['potential_loss']}
""".strip()