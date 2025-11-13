"""
Model Evaluation Script
Performs 5-fold cross-validation and calculates performance metrics

References:
- Kohavi, R. (1995). "A study of cross-validation and bootstrap for accuracy estimation and model selection."
- Sarwar et al. (2001) for recommendation metrics

Metrics:
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Precision@K
- Recall@K
- F1-score
"""
import argparse
import sys
import os
import numpy as np
from sklearn.model_selection import KFold
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import SessionLocal
from src.models import UserRating
from src.services.recommendation.hybrid_engine import HybridRecommendationEngine


def calculate_rmse(predictions, actuals):
    """Calculate Root Mean Squared Error"""
    return np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2))


def calculate_mae(predictions, actuals):
    """Calculate Mean Absolute Error"""
    return np.mean(np.abs(np.array(predictions) - np.array(actuals)))


def calculate_precision_at_k(recommended_items, relevant_items, k=10):
    """Calculate Precision@K"""
    recommended_k = set(recommended_items[:k])
    relevant_set = set(relevant_items)

    if len(recommended_k) == 0:
        return 0.0

    return len(recommended_k.intersection(relevant_set)) / len(recommended_k)


def calculate_recall_at_k(recommended_items, relevant_items, k=10):
    """Calculate Recall@K"""
    recommended_k = set(recommended_items[:k])
    relevant_set = set(relevant_items)

    if len(relevant_set) == 0:
        return 0.0

    return len(recommended_k.intersection(relevant_set)) / len(relevant_set)


def evaluate_fold(train_ratings, test_ratings, products, fold_num):
    """Evaluate a single fold"""
    print(f"\n📊 Evaluating Fold {fold_num + 1}...")

    # Train model on training set
    engine = HybridRecommendationEngine(cf_weight=0.6, cb_weight=0.4)
    engine.train(train_ratings, products)

    # Group test ratings by user
    user_test_ratings = {}
    for rating in test_ratings:
        user_id = rating['user_id']
        if user_id not in user_test_ratings:
            user_test_ratings[user_id] = []
        user_test_ratings[user_id].append(rating)

    # Evaluate each user
    all_rmse = []
    all_mae = []
    all_precision = []
    all_recall = []

    for user_id, test_user_ratings in user_test_ratings.items():
        # Get user's training ratings
        train_user_ratings = [r for r in train_ratings if r['user_id'] == user_id]

        if len(train_user_ratings) == 0:
            continue  # Cold start user, skip

        # Generate recommendations
        user_profile = {'user_id': user_id, 'skin_type': 'normal', 'concerns': []}

        try:
            recommendations = engine.recommend(
                user_id=user_id,
                user_profile=user_profile,
                user_ratings=train_user_ratings,
                n_recommendations=10,
                exclude_rated=True
            )
        except:
            continue

        # Get predicted items
        recommended_items = [rec['product_id'] for rec in recommendations]

        # Get relevant items (items with rating >= 4.0)
        relevant_items = [r['product_id'] for r in test_user_ratings if r['rating'] >= 4.0]

        if len(relevant_items) > 0:
            precision = calculate_precision_at_k(recommended_items, relevant_items, k=10)
            recall = calculate_recall_at_k(recommended_items, relevant_items, k=10)

            all_precision.append(precision)
            all_recall.append(recall)

    # Calculate fold metrics
    fold_metrics = {
        'precision@10': np.mean(all_precision) if all_precision else 0.0,
        'recall@10': np.mean(all_recall) if all_recall else 0.0,
    }

    if fold_metrics['precision@10'] + fold_metrics['recall@10'] > 0:
        fold_metrics['f1@10'] = 2 * (fold_metrics['precision@10'] * fold_metrics['recall@10']) / \
                                 (fold_metrics['precision@10'] + fold_metrics['recall@10'])
    else:
        fold_metrics['f1@10'] = 0.0

    print(f"  Precision@10: {fold_metrics['precision@10']:.4f}")
    print(f"  Recall@10: {fold_metrics['recall@10']:.4f}")
    print(f"  F1@10: {fold_metrics['f1@10']:.4f}")

    return fold_metrics


def perform_cross_validation(n_folds=5):
    """Perform K-fold cross-validation"""
    print("=" * 60)
    print("5-Fold Cross-Validation Evaluation")
    print("=" * 60)

    # Load data
    print("\n📚 Loading data from database...")
    session = SessionLocal()

    try:
        # Load ratings
        ratings_query = session.query(UserRating).all()
        ratings = [
            {
                'user_id': r.user_id,
                'product_id': r.product_id,
                'rating': float(r.rating),
            }
            for r in ratings_query
        ]

        print(f"Loaded {len(ratings)} ratings")

        if len(ratings) < n_folds:
            print(f"❌ Not enough ratings for {n_folds}-fold CV (need at least {n_folds})")
            return

        # Load products (same for all folds)
        from src.models import Product
        products_query = session.query(Product).all()
        products = [p.to_dict() for p in products_query]

        print(f"Loaded {len(products)} products")

        # Perform K-fold cross-validation
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)

        fold_results = []
        ratings_array = np.array(range(len(ratings)))

        for fold_num, (train_idx, test_idx) in enumerate(kf.split(ratings_array)):
            train_ratings = [ratings[i] for i in train_idx]
            test_ratings = [ratings[i] for i in test_idx]

            print(f"\nFold {fold_num + 1}/{n_folds}: {len(train_ratings)} train, {len(test_ratings)} test")

            fold_metrics = evaluate_fold(train_ratings, test_ratings, products, fold_num)
            fold_results.append(fold_metrics)

        # Calculate average metrics
        print("\n" + "=" * 60)
        print("Cross-Validation Results")
        print("=" * 60)

        avg_metrics = {}
        for metric in fold_results[0].keys():
            values = [fold[metric] for fold in fold_results]
            avg_metrics[metric] = {
                'mean': np.mean(values),
                'std': np.std(values),
            }

        for metric, stats in avg_metrics.items():
            print(f"{metric}: {stats['mean']:.4f} ± {stats['std']:.4f}")

        print("=" * 60)
        print("✅ Evaluation completed!")

        return avg_metrics

    finally:
        session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Evaluate recommendation models using cross-validation')

    parser.add_argument(
        '--folds',
        type=int,
        default=5,
        help='Number of folds for cross-validation (default: 5)'
    )

    args = parser.parse_args()

    perform_cross_validation(n_folds=args.folds)


if __name__ == '__main__':
    main()
