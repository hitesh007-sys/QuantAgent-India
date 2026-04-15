def compute_risk(
    entry_price: float,
    direction: str,
    rr_ratio: float = 1.5
) -> dict:
    """
    Computes stop loss and take profit levels.
    direction: 'BUY' or 'SELL'
    rr_ratio: risk reward ratio between 1.2 and 1.8
    """
    # Fixed stop loss of 0.05% as per QuantAgent paper
    stop_loss_pct    = 0.0005
    take_profit_pct  = stop_loss_pct * rr_ratio

    if direction == "BUY":
        stop_loss   = round(entry_price * (1 - stop_loss_pct), 2)
        take_profit = round(entry_price * (1 + take_profit_pct), 2)
    else:
        stop_loss   = round(entry_price * (1 + stop_loss_pct), 2)
        take_profit = round(entry_price * (1 - take_profit_pct), 2)

    # Risk level based on rr_ratio
    if rr_ratio >= 1.6:
        risk_level = "Low"
    elif rr_ratio >= 1.3:
        risk_level = "Medium"
    else:
        risk_level = "High"

    potential_profit = round(abs(take_profit - entry_price), 2)
    potential_loss   = round(abs(stop_loss - entry_price), 2)

    return {
        "direction":       direction,
        "entry":           entry_price,
        "stop_loss":       stop_loss,
        "take_profit":     take_profit,
        "rr_ratio":        rr_ratio,
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