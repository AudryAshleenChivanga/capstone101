"""
Advanced Reinforcement Learning for Capsule Endoscopy Simulation
Multi-class detection: H. pylori, Peptic Ulcer, Gastric Cancer, Tumors
Real-time learning with visual feedback
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import random
from datetime import datetime


class GastricEnvironment:
    """
    3D Gastric environment for capsule endoscopy simulation
    Simulates different pathological conditions and tissue characteristics
    """
    
    # Pathological conditions
    CONDITIONS = {
        'healthy': {'color': (255, 200, 170), 'severity': 0.0},
        'h_pylori': {'color': (255, 150, 150), 'severity': 0.4},
        'peptic_ulcer': {'color': (200, 50, 50), 'severity': 0.7},
        'gastric_cancer': {'color': (150, 0, 0), 'severity': 0.9},
        'tumor': {'color': (100, 0, 50), 'severity': 0.85},
        'inflammation': {'color': (255, 100, 100), 'severity': 0.3}
    }
    
    def __init__(self, scenario: str = 'mixed'):
        self.grid_size = 15  # 15x15x3 layers (3D representation)
        self.depth_layers = 3  # Surface, middle, deep tissue
        self.scenario = scenario
        self.tissue_map = self._generate_tissue_map()
        self.capsule_position = {'x': 7, 'y': 7, 'z': 0}  # Start at surface center
        self.capsule_path = []
        self.images_captured = []
        self.detections = []
        self.step_count = 0
        self.max_steps = 100
        
    def _generate_tissue_map(self) -> np.ndarray:
        """Generate 3D tissue map with pathological conditions"""
        tissue_map = np.zeros((self.grid_size, self.grid_size, self.depth_layers, 2))
        # Last dimension: [condition_type, severity]
        
        if self.scenario == 'healthy':
            # Mostly healthy tissue
            tissue_map[:, :, :, 0] = 0  # Healthy
            tissue_map[:, :, :, 1] = np.random.uniform(0, 0.2, 
                (self.grid_size, self.grid_size, self.depth_layers))
                
        elif self.scenario == 'h_pylori':
            # H. pylori infection clusters
            num_clusters = random.randint(3, 5)
            for _ in range(num_clusters):
                cx, cy = random.randint(2, 12), random.randint(2, 12)
                for i in range(max(0, cx-2), min(self.grid_size, cx+3)):
                    for j in range(max(0, cy-2), min(self.grid_size, cy+3)):
                        distance = np.sqrt((i-cx)**2 + (j-cy)**2)
                        tissue_map[i, j, :, 0] = 1  # H. pylori
                        tissue_map[i, j, :, 1] = 0.4 + 0.3 * np.exp(-distance/2)
                        
        elif self.scenario == 'peptic_ulcer':
            # Peptic ulcer with surrounding inflammation
            ux, uy = random.randint(5, 10), random.randint(5, 10)
            for i in range(max(0, ux-3), min(self.grid_size, ux+4)):
                for j in range(max(0, uy-3), min(self.grid_size, uy+4)):
                    distance = np.sqrt((i-ux)**2 + (j-uy)**2)
                    if distance < 2:
                        tissue_map[i, j, :, 0] = 2  # Peptic ulcer
                        tissue_map[i, j, :, 1] = 0.7 + 0.2 * (1 - distance/2)
                    else:
                        tissue_map[i, j, :, 0] = 5  # Inflammation
                        tissue_map[i, j, :, 1] = 0.3 * np.exp(-distance/3)
                        
        elif self.scenario == 'gastric_cancer':
            # Cancerous tissue with irregular borders
            cx, cy = random.randint(4, 11), random.randint(4, 11)
            for i in range(max(0, cx-4), min(self.grid_size, cx+5)):
                for j in range(max(0, cy-4), min(self.grid_size, cy+5)):
                    distance = np.sqrt((i-cx)**2 + (j-cy)**2)
                    irregularity = random.uniform(0.7, 1.3)
                    if distance * irregularity < 3:
                        tissue_map[i, j, :, 0] = 3  # Gastric cancer
                        tissue_map[i, j, :, 1] = 0.9
                        
        elif self.scenario == 'tumor':
            # Solid tumor mass
            tx, ty = random.randint(5, 10), random.randint(5, 10)
            for i in range(max(0, tx-2), min(self.grid_size, tx+3)):
                for j in range(max(0, ty-2), min(self.grid_size, ty+3)):
                    distance = np.sqrt((i-tx)**2 + (j-ty)**2)
                    if distance < 2.5:
                        tissue_map[i, j, :, 0] = 4  # Tumor
                        tissue_map[i, j, :, 1] = 0.85
                        
        else:  # 'mixed' - combination of conditions
            # Add multiple pathologies
            # H. pylori cluster
            cx, cy = random.randint(2, 6), random.randint(2, 6)
            for i in range(max(0, cx-2), min(self.grid_size, cx+3)):
                for j in range(max(0, cy-2), min(self.grid_size, cy+3)):
                    tissue_map[i, j, 0, 0] = 1
                    tissue_map[i, j, 0, 1] = 0.5
            
            # Peptic ulcer
            ux, uy = random.randint(8, 12), random.randint(8, 12)
            for i in range(max(0, ux-2), min(self.grid_size, ux+3)):
                for j in range(max(0, uy-2), min(self.grid_size, uy+3)):
                    tissue_map[i, j, 1, 0] = 2
                    tissue_map[i, j, 1, 1] = 0.7
            
            # Small tumor
            tx, ty = random.randint(4, 8), random.randint(9, 13)
            for i in range(max(0, tx-1), min(self.grid_size, tx+2)):
                for j in range(max(0, ty-1), min(self.grid_size, ty+2)):
                    tissue_map[i, j, 2, 0] = 4
                    tissue_map[i, j, 2, 1] = 0.8
        
        return tissue_map
    
    def reset(self) -> Dict:
        """Reset environment"""
        self.tissue_map = self._generate_tissue_map()
        self.capsule_position = {'x': 7, 'y': 7, 'z': 0}
        self.capsule_path = [self.capsule_position.copy()]
        self.images_captured = []
        self.detections = []
        self.step_count = 0
        return self.get_state()
    
    def get_state(self) -> Dict:
        """Get current state"""
        x, y, z = self.capsule_position['x'], self.capsule_position['y'], self.capsule_position['z']
        
        # Get local tissue view (5x5 window)
        local_view = []
        for i in range(max(0, x-2), min(self.grid_size, x+3)):
            for j in range(max(0, y-2), min(self.grid_size, y+3)):
                condition = int(self.tissue_map[i, j, z, 0])
                severity = float(self.tissue_map[i, j, z, 1])
                local_view.append({'condition': condition, 'severity': severity})
        
        current_tissue = self.tissue_map[x, y, z]
        
        return {
            'position': self.capsule_position.copy(),
            'local_view': local_view,
            'current_condition': int(current_tissue[0]),
            'current_severity': float(current_tissue[1]),
            'images_captured': len(self.images_captured),
            'steps_taken': self.step_count
        }
    
    def step(self, action: str) -> Tuple[Dict, float, bool]:
        """
        Execute action: move_up, move_down, move_left, move_right, 
                       move_deeper, move_surface, capture_image
        """
        self.step_count += 1
        x, y, z = self.capsule_position['x'], self.capsule_position['y'], self.capsule_position['z']
        reward = -0.05  # Small penalty for each step
        
        # Movement actions
        if action == 'move_up' and x > 0:
            self.capsule_position['x'] -= 1
        elif action == 'move_down' and x < self.grid_size - 1:
            self.capsule_position['x'] += 1
        elif action == 'move_left' and y > 0:
            self.capsule_position['y'] -= 1
        elif action == 'move_right' and y < self.grid_size - 1:
            self.capsule_position['y'] += 1
        elif action == 'move_deeper' and z < self.depth_layers - 1:
            self.capsule_position['z'] += 1
        elif action == 'move_surface' and z > 0:
            self.capsule_position['z'] -= 1
        elif action == 'capture_image':
            # Capture image at current location
            tissue = self.tissue_map[x, y, z]
            condition_type = int(tissue[0])
            severity = float(tissue[1])
            
            image_data = {
                'position': self.capsule_position.copy(),
                'condition': list(self.CONDITIONS.keys())[condition_type],
                'severity': severity,
                'timestamp': self.step_count
            }
            
            self.images_captured.append(image_data)
            
            # Reward based on finding pathology
            if condition_type > 0:  # Pathology found
                reward = severity * 10  # Higher reward for more severe conditions
                
                # Bonus for correct diagnosis
                if severity > 0.6:  # Significant pathology
                    reward += 5
                    self.detections.append(image_data)
        
        self.capsule_path.append(self.capsule_position.copy())
        
        # Check if done
        done = (
            self.step_count >= self.max_steps or
            len(self.detections) >= 5  # Found enough pathologies
        )
        
        next_state = self.get_state()
        return next_state, reward, done


class CapsuleRLAgent:
    """
    Deep Q-Learning agent for capsule endoscopy navigation
    Learns optimal paths to detect pathologies
    """
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.3):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.actions = ['move_up', 'move_down', 'move_left', 'move_right', 
                       'move_deeper', 'move_surface', 'capture_image']
        self.episode_count = 0
        self.episode_rewards = []
        self.detection_accuracy = []
        
    def _state_to_key(self, state: Dict) -> str:
        """Convert state to hashable key"""
        pos = state['position']
        condition = state['current_condition']
        severity = round(state['current_severity'], 1)
        return f"{pos['x']},{pos['y']},{pos['z']},{condition},{severity}"
    
    def get_action(self, state: Dict, training: bool = True) -> str:
        """Epsilon-greedy action selection"""
        state_key = self._state_to_key(state)
        
        # Exploration
        if training and random.random() < self.epsilon:
            # Smart exploration: prefer capture when severity is high
            if state['current_severity'] > 0.5 and random.random() > 0.5:
                return 'capture_image'
            return random.choice(self.actions)
        
        # Exploitation
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in self.actions}
        
        q_values = self.q_table[state_key]
        max_q = max(q_values.values())
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def update(self, state: Dict, action: str, reward: float, next_state: Dict, done: bool):
        """Q-learning update"""
        state_key = self._state_to_key(state)
        next_key = self._state_to_key(next_state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in self.actions}
        if next_key not in self.q_table:
            self.q_table[next_key] = {a: 0.0 for a in self.actions}
        
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_key].values()) if not done else 0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
    
    def train_episode(self, env: GastricEnvironment) -> Dict:
        """Train for one episode"""
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            action = self.get_action(state, training=True)
            next_state, reward, done = env.step(action)
            self.update(state, action, reward, next_state, done)
            
            episode_reward += reward
            state = next_state
        
        self.episode_count += 1
        self.episode_rewards.append(episode_reward)
        
        # Calculate detection accuracy
        true_positives = len(env.detections)
        total_pathologies = np.sum(env.tissue_map[:, :, :, 1] > 0.5)
        accuracy = true_positives / max(total_pathologies, 1)
        self.detection_accuracy.append(accuracy)
        
        # Decay epsilon
        self.epsilon = max(0.05, self.epsilon * 0.995)
        
        return {
            'episode': self.episode_count,
            'reward': episode_reward,
            'detections': len(env.detections),
            'images': len(env.images_captured),
            'accuracy': accuracy,
            'epsilon': self.epsilon
        }


def simulate_capsule_endoscopy(scenario: str = 'mixed', num_steps: int = 80) -> Dict:
    """
    Run capsule endoscopy simulation with trained agent
    """
    # Quick training (10 episodes)
    agent = CapsuleRLAgent()
    env = GastricEnvironment(scenario=scenario)
    
    print(f"Training agent on {scenario} scenario...")
    training_log = []
    for i in range(10):
        metrics = agent.train_episode(env)
        training_log.append(metrics)
        if i % 5 == 0:
            print(f"Episode {i}: Reward={metrics['reward']:.2f}, Detections={metrics['detections']}, Accuracy={metrics['accuracy']:.2f}")
    
    # Run final simulation
    print("\nRunning final capsule endoscopy...")
    env.reset()
    state = env.get_state()
    procedure_log = []
    done = False
    step = 0
    
    while not done and step < num_steps:
        action = agent.get_action(state, training=False)
        next_state, reward, done = env.step(action)
        
        procedure_log.append({
            'step': step,
            'action': action,
            'position': state['position'].copy(),
            'condition': state['current_condition'],
            'severity': state['current_severity'],
            'reward': round(float(reward), 2)
        })
        
        state = next_state
        step += 1
    
    # Generate clinical report
    detections_by_type = {}
    for detection in env.detections:
        condition = detection['condition']
        if condition not in detections_by_type:
            detections_by_type[condition] = []
        detections_by_type[condition].append(detection)
    
    return {
        'scenario': scenario,
        'training_log': training_log,
        'procedure_log': procedure_log,
        'capsule_path': env.capsule_path,
        'images_captured': env.images_captured,
        'detections': env.detections,
        'detections_by_type': detections_by_type,
        'total_steps': step,
        'agent_metrics': {
            'total_states_learned': len(agent.q_table),
            'final_epsilon': agent.epsilon,
            'average_reward': np.mean(agent.episode_rewards[-5:]) if agent.episode_rewards else 0
        }
    }


if __name__ == "__main__":
    result = simulate_capsule_endoscopy('mixed', 60)
    print(f"\nSimulation complete!")
    print(f"Images captured: {len(result['images_captured'])}")
    print(f"Pathologies detected: {len(result['detections'])}")
    print(f"Detection types: {list(result['detections_by_type'].keys())}")

