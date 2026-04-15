import sys
sys.path.append('tools')

from compute_indicators import load_stock, compute_indicators, interpret_indicators

df = load_stock('RELIANCE')
print('Data loaded:', len(df), 'rows')

indicators = compute_indicators(df)
print('\nIndicator values:')
for k, v in indicators.items():
    print(f'  {k}: {v}')

print('\nPlain English summary:')
print(interpret_indicators(indicators))