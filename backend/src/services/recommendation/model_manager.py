"""
Model Manager
Handles model versioning, loading, and metadata tracking using joblib
"""
import os
import joblib
import json
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages ML model versions and metadata

    Features:
    - Load/save models with joblib
    - Version tracking with metadata
    - Model registry
    """

    def __init__(self, models_dir='models'):
        """
        Initialize model manager

        Args:
            models_dir: Directory to store models
        """
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def save_model(self, model, version: str, metadata: Optional[Dict] = None):
        """
        Save model with version and metadata

        Args:
            model: Model object to save
            version: Version string (e.g., 'v1.0.0')
            metadata: Optional metadata dictionary

        Returns:
            Path to saved model file
        """
        # Create model filename
        model_filename = f"recommendation_{version}.joblib"
        model_path = os.path.join(self.models_dir, model_filename)

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata.update({
            'version': version,
            'saved_at': datetime.utcnow().isoformat(),
            'model_type': type(model).__name__,
        })

        # Save model and metadata together
        model_data = {
            'model': model,
            'metadata': metadata,
        }

        joblib.dump(model_data, model_path)

        # Also save metadata separately as JSON
        metadata_path = model_path.replace('.joblib', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model saved: {model_path}")
        logger.info(f"Metadata saved: {metadata_path}")

        # Update latest symlink
        self._update_latest_link(model_filename)

        return model_path

    def load_model(self, version: str = 'latest'):
        """
        Load model by version

        Args:
            version: Version string or 'latest'

        Returns:
            Tuple of (model, metadata)
        """
        if version == 'latest':
            model_path = os.path.join(self.models_dir, 'recommendation_latest.joblib')
        else:
            model_filename = f"recommendation_{version}.joblib"
            model_path = os.path.join(self.models_dir, model_filename)

        if not os.path.exists(model_path):
            logger.error(f"Model not found: {model_path}")
            return None, None

        # Load model data
        model_data = joblib.load(model_path)

        if isinstance(model_data, dict):
            model = model_data.get('model')
            metadata = model_data.get('metadata', {})
        else:
            # Legacy format (just model)
            model = model_data
            metadata = {}

        logger.info(f"Model loaded: {model_path} (version: {metadata.get('version', 'unknown')})")

        return model, metadata

    def list_models(self):
        """
        List all saved models

        Returns:
            List of model metadata dictionaries
        """
        models = []

        for filename in os.listdir(self.models_dir):
            if filename.endswith('_metadata.json'):
                metadata_path = os.path.join(self.models_dir, filename)

                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                metadata['filename'] = filename.replace('_metadata.json', '.joblib')
                models.append(metadata)

        # Sort by version
        models.sort(key=lambda x: x.get('saved_at', ''), reverse=True)

        return models

    def get_model_info(self, version: str = 'latest') -> Optional[Dict]:
        """
        Get metadata for a specific model version

        Args:
            version: Version string or 'latest'

        Returns:
            Metadata dictionary or None
        """
        if version == 'latest':
            metadata_path = os.path.join(self.models_dir, 'recommendation_latest_metadata.json')
        else:
            metadata_filename = f"recommendation_{version}_metadata.json"
            metadata_path = os.path.join(self.models_dir, metadata_filename)

        if not os.path.exists(metadata_path):
            logger.warning(f"Metadata not found: {metadata_path}")
            return None

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return metadata

    def _update_latest_link(self, model_filename: str):
        """
        Update 'latest' symlink to point to newest model

        Args:
            model_filename: Filename of the latest model
        """
        latest_path = os.path.join(self.models_dir, 'recommendation_latest.joblib')
        target_path = os.path.join(self.models_dir, model_filename)

        # Remove existing latest file
        if os.path.exists(latest_path):
            os.remove(latest_path)

        # Copy file (symlinks don't work well cross-platform)
        import shutil
        shutil.copy2(target_path, latest_path)

        # Also copy metadata
        latest_meta = latest_path.replace('.joblib', '_metadata.json')
        target_meta = target_path.replace('.joblib', '_metadata.json')

        if os.path.exists(latest_meta):
            os.remove(latest_meta)

        if os.path.exists(target_meta):
            shutil.copy2(target_meta, latest_meta)

        logger.info(f"Updated 'latest' to point to {model_filename}")


# Global model manager instance
model_manager = ModelManager()
