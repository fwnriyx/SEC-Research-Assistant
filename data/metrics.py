def calculate_score(fin, pm):
    score = 0
    breakdown = {}

    # Revenue Growth (20 pts)
    rg = (fin["revenue_growth"] or 0) * 100
    if rg > 20:      pts = 20
    elif rg > 10:    pts = 15
    elif rg > 0:     pts = 10
    else:            pts = 0
    score += pts
    breakdown["Revenue Growth"] = pts

    # Free Cash Flow (20 pts)
    pts = 20 if (fin["fcf"] or 0) > 0 else 0
    score += pts
    breakdown["Free Cash Flow"] = pts

    # Debt/Equity (15 pts)
    de = fin["debt_to_equity"] or 999
    if de < 50:      pts = 15
    elif de < 100:   pts = 10
    else:            pts = 0
    score += pts
    breakdown["Debt/Equity"] = pts

    # Return on Equity (15 pts)
    roe = (fin["roic"] or 0) * 100
    if roe > 20:     pts = 15
    elif roe > 10:   pts = 10
    else:            pts = 0
    score += pts
    breakdown["Return on Equity"] = pts

    # Sharpe Ratio (15 pts)
    sharpe = pm["sharpe_ratio"]
    if sharpe > 1:   pts = 15
    elif sharpe > 0: pts = 10
    else:            pts = 0
    score += pts
    breakdown["Sharpe Ratio"] = pts

    # Max Drawdown (15 pts)
    dd = pm["max_drawdown"]
    if dd > -15:     pts = 15
    elif dd > -25:   pts = 10
    elif dd > -35:   pts = 5
    else:            pts = 0
    score += pts
    breakdown["Max Drawdown"] = pts

    return score, breakdown


def get_rating(score):
    if score >= 80:   
        return "🟢 Strong Buy"
    elif score >= 65: 
        return "🟡 Buy"
    elif score >= 50: 
        return "🟠 Hold"
    else:             
        return "🔴 Avoid"