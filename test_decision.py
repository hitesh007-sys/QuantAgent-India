import sys
sys.path.append('tools')
sys.path.append('agents')

from decision_agent import run_decision_agent, format_final_output

print("Testing DecisionAgent...\n")

# Test with Reliance
result = run_decision_agent('RELIANCE')
print(format_final_output(result))

print("\n")

# Test with TCS
result2 = run_decision_agent('TCS')
print(format_final_output(result2))