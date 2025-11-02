"""
Reinforcement Learning Model for 3D Endoscopy/Biopsy Simulation
Uses Q-Learning for optimal biopsy site selection and tissue analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import random


class BiopsyEnvironment:
    """
    Simulates the gastric environment for endoscopy procedure
    State space: tissue characteristics, biopsy locations, visual features
    Action space: move endoscope, take biopsy, analyze tissue
    """
    
    def __init__(self):
        self.grid_size = 10  # 10x10 grid representing gastric tissue
        self.current_position = (5, 5)  # Center starting position
        self.biopsy_sites = self._generate_tissue_grid()
        self.steps_taken = 0
        self.max_steps = 50
        self.biopsies_collected = []
        
    def _generate_tissue_grid(self) -> np.ndarray:
        """Generate tissue grid with varying infection probabilities"""
        # Create base grid
        grid = np.random.random((self.grid_size, self.grid_size))
        
        # Add infection hotspots (H. pylori colonies)
        num_hotspots = random.randint(2, 4)
        for _ in range(num_hotspots):
            center_x = random.randint(1, self.grid_size - 2)
            center_y = random.randint(1, self.grid_size - 2)
            
            # Create gaussian distribution around hotspot
            for i in range(max(0, center_x-2), min(self.grid_size, center_x+3)):
                for j in range(max(0, center_y-2), min(self.grid_size, center_y+3)):
                    distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
                    grid[i, j] = min(1.0, grid[i, j] + 0.8 * np.exp(-distance/2))
        
        return grid
    
    def reset(self) -> Dict:
        """Reset environment to initial state"""
        self.current_position = (5, 5)
        self.steps_taken = 0
        self.biopsies_collected = []
        self.biopsy_sites = self._generate_tissue_grid()
        return self.get_state()
    
    def get_state(self) -> Dict:
        """Get current state representation"""
        x, y = self.current_position
        
        # Local tissue view (3x3 window around current position)
        local_view = []
        for i in range(max(0, x-1), min(self.grid_size, x+2)):
            for j in range(max(0, y-1), min(self.grid_size, y+2)):
                local_view.append(float(self.biopsy_sites[i, j]))
        
        return {
            'position': self.current_position,
            'local_tissue_density': local_view,
            'current_site_value': float(self.biopsy_sites[x, y]),
            'steps_remaining': self.max_steps - self.steps_taken,
            'biopsies_collected': len(self.biopsies_collected)
        }
    
    def step(self, action: str) -> Tuple[Dict, float, bool]:
        """
        Execute action and return (next_state, reward, done)
        Actions: 'up', 'down', 'left', 'right', 'biopsy'
        """
        self.steps_taken += 1
        x, y = self.current_position
        reward = -0.1  # Small penalty for each step
        
        # Movement actions
        if action == 'up' and x > 0:
            self.current_position = (x - 1, y)
        elif action == 'down' and x < self.grid_size - 1:
            self.current_position = (x + 1, y)
        elif action == 'left' and y > 0:
            self.current_position = (x, y - 1)
        elif action == 'right' and y < self.grid_size - 1:
            self.current_position = (x, y + 1)
        elif action == 'biopsy':
            # Take biopsy at current location
            tissue_value = self.biopsy_sites[x, y]
            self.biopsies_collected.append({
                'position': (x, y),
                'infection_probability': float(tissue_value),
                'tissue_quality': 'high' if tissue_value > 0.6 else 'medium' if tissue_value > 0.3 else 'low'
            })
            # Reward based on tissue value (high infection areas are valuable)
            reward = tissue_value * 10
            
            # Mark site as sampled
            self.biopsy_sites[x, y] = self.biopsy_sites[x, y] * 0.5
        
        # Check if done
        done = (
            self.steps_taken >= self.max_steps or 
            len(self.biopsies_collected) >= 4  # Optimal number of biopsies
        )
        
        next_state = self.get_state()
        return next_state, reward, done


class QLearningAgent:
    """
    Q-Learning agent for optimal biopsy site selection
    Learns to navigate gastric tissue and identify high-value biopsy locations
    """
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.2):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.actions = ['up', 'down', 'left', 'right', 'biopsy']
        self.training_episodes = 0
        
    def _state_to_key(self, state: Dict) -> str:
        """Convert state dict to hashable key"""
        pos = state['position']
        tissue_val = round(state['current_site_value'], 1)
        biopsies = state['biopsies_collected']
        return f"{pos[0]},{pos[1]},{tissue_val},{biopsies}"
    
    def get_action(self, state: Dict, training: bool = True) -> str:
        """
        Select action using epsilon-greedy policy
        """
        state_key = self._state_to_key(state)
        
        # Exploration vs Exploitation
        if training and random.random() < self.epsilon:
            return random.choice(self.actions)
        
        # Get Q-values for all actions
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in self.actions}
        
        q_values = self.q_table[state_key]
        
        # Choose action with highest Q-value
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def update(self, state: Dict, action: str, reward: float, next_state: Dict, done: bool):
        """Update Q-table using Q-learning update rule"""
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Initialize Q-values if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in self.actions}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {a: 0.0 for a in self.actions}
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key].values()) if not done else 0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
    
    def train(self, episodes: int = 1000):
        """Train the agent"""
        env = BiopsyEnvironment()
        rewards_history = []
        
        for episode in range(episodes):
            state = env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                action = self.get_action(state, training=True)
                next_state, reward, done = env.step(action)
                self.update(state, action, reward, next_state, done)
                
                episode_reward += reward
                state = next_state
            
            rewards_history.append(episode_reward)
            self.training_episodes += 1
            
            # Decay epsilon (reduce exploration over time)
            if episode % 100 == 0:
                self.epsilon = max(0.05, self.epsilon * 0.95)
        
        return rewards_history


class BiopsyAnalyzer:
    """
    Analyzes biopsy results and provides clinical recommendations
    """
    
    @staticmethod
    def analyze_biopsies(biopsies: List[Dict]) -> Dict:
        """
        Analyze collected biopsies and generate clinical report
        """
        if not biopsies:
            return {
                'status': 'insufficient',
                'message': 'No biopsies collected',
                'recommendation': 'Collect at least 2-4 biopsy samples'
            }
        
        # Calculate aggregate metrics
        avg_infection_prob = np.mean([b['infection_probability'] for b in biopsies])
        max_infection_prob = max([b['infection_probability'] for b in biopsies])
        
        # Classify infection severity
        if max_infection_prob > 0.7:
            severity = 'High'
            recommendation = 'Triple therapy recommended: PPI + Clarithromycin + Amoxicillin for 14 days'
            risk_level = 'high'
        elif max_infection_prob > 0.4:
            severity = 'Moderate'
            recommendation = 'Standard dual therapy: PPI + Amoxicillin for 10-14 days. Consider follow-up biopsy.'
            risk_level = 'moderate'
        else:
            severity = 'Low'
            recommendation = 'Monitor symptoms. Repeat endoscopy if symptoms persist.'
            risk_level = 'low'
        
        # Identify optimal biopsy sites
        high_quality_sites = [
            b for b in biopsies 
            if b['tissue_quality'] == 'high' and b['infection_probability'] > 0.5
        ]
        
        return {
            'status': 'complete',
            'total_biopsies': len(biopsies),
            'average_infection_probability': round(float(avg_infection_prob), 3),
            'maximum_infection_probability': round(float(max_infection_prob), 3),
            'severity': severity,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'high_quality_samples': len(high_quality_sites),
            'biopsy_details': biopsies,
            'confidence': min(0.95, 0.6 + (len(biopsies) * 0.1)),
            'findings': {
                'h_pylori_detected': max_infection_prob > 0.3,
                'inflammation_present': avg_infection_prob > 0.25,
                'sample_quality': 'Adequate' if len(biopsies) >= 2 else 'Marginal',
                'tissue_integrity': 'Good' if len(high_quality_sites) >= 1 else 'Fair'
            },
            'timestamp': datetime.now().isoformat()
        }


# Global agent instance (pre-trained)
global_agent = QLearningAgent()
print("Training RL agent for optimal biopsy site selection...")
training_rewards = global_agent.train(episodes=500)
print(f"Agent trained. Final epsilon: {global_agent.epsilon:.3f}")
print(f"Average reward (last 100 episodes): {np.mean(training_rewards[-100:]):.2f}")


def simulate_biopsy_procedure(num_steps: int = 30) -> Dict:
    """
    Run a complete biopsy simulation using trained RL agent
    """
    env = BiopsyEnvironment()
    state = env.reset()
    
    procedure_log = []
    done = False
    step = 0
    
    while not done and step < num_steps:
        # Agent selects action
        action = global_agent.get_action(state, training=False)
        
        # Execute action
        next_state, reward, done = env.step(action)
        
        # Log step
        procedure_log.append({
            'step': step,
            'action': action,
            'position': state['position'],
            'tissue_value': state['current_site_value'],
            'reward': round(float(reward), 2)
        })
        
        state = next_state
        step += 1
    
    # Analyze results
    analysis = BiopsyAnalyzer.analyze_biopsies(env.biopsies_collected)
    
    return {
        'procedure_log': procedure_log,
        'biopsies_collected': env.biopsies_collected,
        'analysis': analysis,
        'total_steps': step,
        'agent_performance': {
            'total_reward': sum([log['reward'] for log in procedure_log]),
            'efficiency': len(env.biopsies_collected) / step if step > 0 else 0
        }
    }


if __name__ == "__main__":
    # Test the simulation
    result = simulate_biopsy_procedure()
    print("\n=== Biopsy Simulation Complete ===")
    print(f"Total biopsies: {len(result['biopsies_collected'])}")
    print(f"Analysis: {result['analysis']['severity']} severity")
    print(f"Recommendation: {result['analysis']['recommendation']}")

