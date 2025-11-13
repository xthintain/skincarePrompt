"""
Model Training Script
Train recommendation models and save to disk with versioning

Usage:
    python scripts/train_recommendation.py --output models/recommendation_v1.0.0.joblib
"""
import argparse
import sys
import os
from datetime import datetime
import joblib
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.recommendation_service import RecommendationService
from src.config import SessionLocal

logger_setup = False


def setup_logging():
    """Setup logging configuration"""
    global logger_setup
    if not logger_setup:
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        logger_setup = True


def train_and_save_model(output_path: str, model_version: str = None):
    """
    Train recommendation model and save to disk

    Args:
        output_path: Path to save the model
        model_version: Version string (e.g., 'v1.0.0')
    """
    setup_logging()
    import logging
    logger = logging.getLogger(__name__)

    logger.info("="  * 60)
    logger.info("Starting Model Training")
    logger.info("=" * 60)

    # Initialize service
    service = RecommendationService()

    # Train models
    logger.info("\n📚 Loading training data...")
    session = SessionLocal()

    try:
        success = service.train_models(session)

        if not success:
            logger.error("❌ Training failed")
            return False

        # Prepare model metadata
        if model_version is None:
            model_version = f"v1.0.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        metadata = {
            'version': model_version,
            'trained_at': datetime.utcnow().isoformat(),
            'cf_weight': service.engine.cf_weight,
            'cb_weight': service.engine.cb_weight,
            'cold_start_threshold': service.engine.cold_start_threshold,
        }

        # Save model and metadata
        model_data = {
            'engine': service.engine,
            'metadata': metadata,
        }

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save using joblib
        joblib.dump(model_data, output_path)
        logger.info(f"\n✅ Model saved to: {output_path}")

        # Save metadata separately as JSON
        metadata_path = output_path.replace('.joblib', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"📝 Metadata saved to: {metadata_path}")

        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("Training Summary")
        logger.info("=" * 60)
        logger.info(f"Model Version: {model_version}")
        logger.info(f"CF Weight: {metadata['cf_weight']}")
        logger.info(f"CB Weight: {metadata['cb_weight']}")
        logger.info(f"Trained at: {metadata['trained_at']}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"\n❌ Error during training: {e}", exc_info=True)
        return False

    finally:
        session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Train recommendation models')

    parser.add_argument(
        '--output',
        type=str,
        default='models/recommendation_latest.joblib',
        help='Output path for trained model (default: models/recommendation_latest.joblib)'
    )

    parser.add_argument(
        '--version',
        type=str,
        default=None,
        help='Model version string (default: auto-generated)'
    )

    args = parser.parse_args()

    # Train and save
    success = train_and_save_model(args.output, args.version)

    if success:
        print("\n✅ Training completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Training failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
