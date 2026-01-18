# basic template for Flask

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.insert(0, '../python')

from ..python.config_models import AppConfig, GenerationParams
from ..python.productcreator import generate_all_product_candidates
from ..python.consoleUI import ConsoleUI

app = Flask(__name__)
CORS(app)

# Disable console output
ConsoleUI.set_verbose(False)
app_config = AppConfig.from_cfg_file('../config/config.cfg')

@app.route('/api/generate', methods=['POST'])
def generate_candidates():
    """Generate candidates with user-specified ranges"""
    data = request.json
    
    try:
        # UI sends: { priceMin: 1, priceMax: 5, priceStep: 0.1, ... }
        params = GenerationParams.from_ui_input(data)
        
        candidates = generate_all_product_candidates(
            params=params,
            app_config=app_config,
            verbose=False  # No console output
        )
        
        return jsonify({
            'status': 'success',
            'count': len(candidates),
            'candidates': [c.to_dict() for c in candidates]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Run optimization in background"""
    data = request.json
    # Start async job, return job_id
    # Client polls /api/status/{job_id}
    pass