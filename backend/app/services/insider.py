import yfinance as yf
from typing import List
from app.models.schemas import InsiderTransaction

def get_corporate_insiders(symbol: str) -> List[InsiderTransaction]:
    """
    Fetch recent corporate insider transactions using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        insider = ticker.insider_transactions
        
        transactions = []
        if insider is not None and not insider.empty:
            # Take top 5 recent transactions
            # yfinance returns: Shares, Value, URL, Text, Insider, Position, Transaction, Start Date, Ownership
            
            for index, row in insider.head(5).iterrows():
                # Note: yfinance column names can vary slightly, being defensive
                try:
                    holder = row.get('Insider', 'Unknown')
                    shares = str(row.get('Shares', '0'))
                    # 'Ownership' often contains "D" or "I"
                    ownership = row.get('Ownership', '')
                    position = "Direct" if "D" in str(ownership) else "Indirect"
                    date = str(row.get('Start Date', ''))
                    text = str(row.get('Text', ''))
                    
                    transactions.append(InsiderTransaction(
                        holder=holder,
                        shares=shares,
                        position=position,
                        date=date,
                        transaction_text=text
                    ))
                except Exception as e:
                    print(f"Error parsing insider row: {e}")
                    continue
                    
        return transactions
    except Exception as e:
        print(f"Error fetching corporate insiders for {symbol}: {e}")
        return []
