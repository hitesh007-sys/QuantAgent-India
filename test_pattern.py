import sys
sys.path.append('tools')
sys.path.append('agents')

from pattern_agent import analyze_pattern

print("Testing PatternAgent...\n")

result = analyze_pattern('RELIANCE')
print("RELIANCE Pattern Analysis:")
print(result)

print("\n" + "="*50 + "\n")

result2 = analyze_pattern('TCS')
print("TCS Pattern Analysis:")
print(result2)