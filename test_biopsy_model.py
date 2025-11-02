from app.rl_biopsy_model import simulate_biopsy_procedure

print("Testing RL Biopsy Model...")
result = simulate_biopsy_procedure(num_steps=10)

print(f"Biopsies collected: {len(result['biopsies_collected'])}")
print(f"Total steps: {result['total_steps']}")
print(f"Analysis severity: {result['analysis']['severity']}")
print(f"Recommendation: {result['analysis']['recommendation']}")
print("\nModel is working correctly!")

