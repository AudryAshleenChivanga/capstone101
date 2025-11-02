"""
Biopsy Simulation API Routes
Provides endpoints for RL-based 3D endoscopy/biopsy simulation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import logging

from app.rl_biopsy_model import simulate_biopsy_procedure, BiopsyEnvironment, global_agent

router = APIRouter(prefix="/biopsy", tags=["Biopsy Simulation"])
logger = logging.getLogger(__name__)


class BiopsySimulationRequest(BaseModel):
    """Request model for biopsy simulation"""
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    simulation_steps: int = Field(30, ge=10, le=100, description="Number of simulation steps")
    difficulty: str = Field("medium", description="Simulation difficulty: easy, medium, hard")


class BiopsySimulationResponse(BaseModel):
    """Response model for biopsy simulation"""
    success: bool
    simulation_id: str
    procedure_log: List[Dict]
    biopsies_collected: List[Dict]
    analysis: Dict
    total_steps: int
    agent_performance: Dict
    timestamp: str


class BiopsyActionRequest(BaseModel):
    """Request for single action in interactive mode"""
    action: str = Field(..., description="Action: up, down, left, right, biopsy")
    current_state: Dict


@router.post("/simulate", response_model=BiopsySimulationResponse)
async def run_biopsy_simulation(
    request: BiopsySimulationRequest
):
    """
    Run complete RL-based biopsy simulation
    
    The RL agent navigates the gastric tissue grid and selects optimal biopsy sites
    based on learned patterns of H. pylori infection distribution.
    """
    try:
        logger.info("Starting biopsy simulation")
        
        # Run simulation with trained RL agent
        result = simulate_biopsy_procedure(num_steps=request.simulation_steps)
        
        # Generate unique simulation ID
        simulation_id = f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        response = BiopsySimulationResponse(
            success=True,
            simulation_id=simulation_id,
            procedure_log=result['procedure_log'],
            biopsies_collected=result['biopsies_collected'],
            analysis=result['analysis'],
            total_steps=result['total_steps'],
            agent_performance=result['agent_performance'],
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Simulation complete: {len(result['biopsies_collected'])} biopsies collected")
        return response
        
    except Exception as e:
        logger.error(f"Biopsy simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/step")
async def execute_biopsy_action(
    request: BiopsyActionRequest
):
    """
    Execute a single action in interactive biopsy mode
    Allows manual control combined with AI suggestions
    """
    try:
        valid_actions = ['up', 'down', 'left', 'right', 'biopsy']
        if request.action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
        
        # Get AI suggestion for current state
        ai_suggestion = global_agent.get_action(request.current_state, training=False)
        
        return {
            'success': True,
            'action_executed': request.action,
            'ai_suggestion': ai_suggestion,
            'confidence': 0.85 if request.action == ai_suggestion else 0.6
        }
        
    except Exception as e:
        logger.error(f"Action execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-stats")
async def get_agent_statistics():
    """
    Get statistics about the trained RL agent
    """
    try:
        return {
            'success': True,
            'agent_info': {
                'type': 'Q-Learning',
                'training_episodes': global_agent.training_episodes,
                'learning_rate': global_agent.learning_rate,
                'discount_factor': global_agent.discount_factor,
                'current_epsilon': global_agent.epsilon,
                'q_table_size': len(global_agent.q_table),
                'actions_available': global_agent.actions
            },
            'performance': {
                'exploration_rate': f"{global_agent.epsilon * 100:.1f}%",
                'exploitation_rate': f"{(1 - global_agent.epsilon) * 100:.1f}%",
                'training_status': 'Trained and Ready'
            }
        }
    except Exception as e:
        logger.error(f"Agent stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-results")
async def analyze_biopsy_results(
    biopsies: List[Dict]
):
    """
    Analyze collected biopsy samples and provide clinical recommendations
    """
    try:
        from app.rl_biopsy_model import BiopsyAnalyzer
        
        analysis = BiopsyAnalyzer.analyze_biopsies(biopsies)
        
        return {
            'success': True,
            'analysis': analysis
        }
        
    except Exception as e:
        logger.error(f"Biopsy analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

