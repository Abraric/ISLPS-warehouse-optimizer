"""
ML Model Training Script for ASLPS.

Trains a Random Forest Classifier to predict optimal storage locations.
Generates synthetic training data and implements all feature engineering logic.
"""
import os
import sys
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trainer for Random Forest storage location prediction model.
    
    Generates synthetic training data and trains model with all features.
    """
    
    def __init__(self, n_samples=5000, random_state=42):
        """
        Initialize trainer.
        
        Args:
            n_samples: Number of training samples to generate
            random_state: Random seed for reproducibility
        """
        self.n_samples = n_samples
        self.random_state = random_state
        self.model = None
        self.feature_names = [
            'usage_frequency',
            'category_similarity',
            'shelf_proximity',
            'pathway_congestion',
            'space_availability',
            'distance_to_entrance',
            'shelf_congestion_score',
            'is_hazardous_match',
            'climate_control_match',
            'weight_utilization',
            'volume_utilization',
            'zone_preference',
        ]
    
    def generate_synthetic_data(self) -> pd.DataFrame:
        """
        Generate synthetic training data.
        
        Simulates realistic warehouse scenarios including all edge cases:
        1. Sudden demand spike
        2. Limited availability
        3. Restricted/Hazard components
        4. New components (cold-start)
        5. Congestion scenarios
        
        Returns:
            DataFrame with features and labels
        """
        logger.info(f"Generating {self.n_samples} synthetic training samples...")
        np.random.seed(self.random_state)
        
        data = []
        
        for i in range(self.n_samples):
            # Simulate component characteristics
            is_hazardous = np.random.choice([0, 1], p=[0.8, 0.2])
            requires_climate = np.random.choice([0, 1], p=[0.7, 0.3])
            category = np.random.choice(['Electronics', 'Mechanical', 'Chemical', 'Raw Materials', 'Finished Goods'])
            
            # Simulate shelf characteristics
            is_hazardous_zone = np.random.choice([0, 1], p=[0.8, 0.2])
            has_climate_control = np.random.choice([0, 1], p=[0.7, 0.3])
            zone = np.random.choice(['A', 'B', 'C', 'D', 'E'])
            
            # Feature 1: Usage frequency (time-decayed)
            # Simulate components with varying usage patterns
            if np.random.random() < 0.3:  # 30% are new components (cold-start)
                usage_frequency = 0.0
            else:
                # Simulate time-decayed frequency
                hours_ago = np.random.exponential(48)  # Exponential distribution
                decay_factor = 0.95
                usage_frequency = min(1.0, decay_factor ** hours_ago * np.random.uniform(0.5, 1.5))
            
            # Feature 2: Category similarity (for cold-start)
            if usage_frequency == 0.0:  # New component
                # Higher similarity score for new components in same category
                category_similarity = np.random.uniform(0.4, 0.8) if category == category else np.random.uniform(0.0, 0.3)
            else:
                category_similarity = np.random.uniform(0.3, 0.9)
            
            # Feature 3: Shelf proximity (graph distance)
            # Closer shelves are better (lower distance)
            distance_to_entrance = np.random.uniform(5, 100)  # 5-100 meters
            shelf_proximity = distance_to_entrance
            
            # Feature 4: Pathway congestion
            # Simulate congestion scenarios (edge case 5)
            if np.random.random() < 0.2:  # 20% high congestion scenarios
                pathway_congestion = np.random.uniform(0.7, 1.0)
            else:
                pathway_congestion = np.random.uniform(0.0, 0.5)
            
            # Feature 5: Space availability (edge case 2)
            if np.random.random() < 0.15:  # 15% limited availability
                space_availability = np.random.uniform(0.0, 0.3)
            else:
                space_availability = np.random.uniform(0.3, 1.0)
            
            # Additional features
            shelf_congestion_score = np.random.uniform(0.0, 1.0)
            is_hazardous_match = 1.0 if (is_hazardous == is_hazardous_zone) else 0.0
            climate_control_match = 1.0 if (requires_climate == has_climate_control) else 0.0
            
            # Weight and volume utilization
            weight_utilization = np.random.uniform(0.0, 0.95)
            volume_utilization = np.random.uniform(0.0, 0.95)
            
            # Zone preference
            zone_preference = np.random.uniform(0.0, 1.0)
            
            # Generate label (optimal = 1, suboptimal = 0)
            # Optimal if:
            # - Matches constraints (hazardous, climate)
            # - Good space availability
            # - Low congestion
            # - Close to entrance
            # - High usage frequency (frequently used items closer)
            optimal_score = 0.0
            
            # Constraint matching (required)
            if is_hazardous_match == 0.0 or climate_control_match == 0.0:
                optimal_score = 0.0  # Cannot be optimal if constraints don't match
            else:
                # Weighted combination
                optimal_score += space_availability * 0.25
                optimal_score += (1.0 - pathway_congestion) * 0.20  # Lower congestion is better
                optimal_score += (1.0 - min(distance_to_entrance / 100, 1.0)) * 0.15  # Closer is better
                optimal_score += usage_frequency * 0.15  # High frequency items closer
                optimal_score += category_similarity * 0.10
                optimal_score += (1.0 - min(weight_utilization, 0.9)) * 0.10  # Less utilization is better
                optimal_score += (1.0 - min(volume_utilization, 0.9)) * 0.05
            
            # Convert to binary label
            is_optimal = 1 if optimal_score > 0.6 else 0
            
            # Edge case: Limited availability - even if optimal, mark as 0 if space is too low
            if space_availability < 0.1:
                is_optimal = 0
            
            # Edge case: High congestion - penalize
            if pathway_congestion > 0.8:
                is_optimal = 0
            
            row = {
                'usage_frequency': usage_frequency,
                'category_similarity': category_similarity,
                'shelf_proximity': shelf_proximity,
                'pathway_congestion': pathway_congestion,
                'space_availability': space_availability,
                'distance_to_entrance': distance_to_entrance,
                'shelf_congestion_score': shelf_congestion_score,
                'is_hazardous_match': is_hazardous_match,
                'climate_control_match': climate_control_match,
                'weight_utilization': weight_utilization,
                'volume_utilization': volume_utilization,
                'zone_preference': zone_preference,
                'is_optimal': is_optimal,
            }
            
            data.append(row)
        
        df = pd.DataFrame(data)
        logger.info(f"Generated {len(df)} samples. Optimal: {df['is_optimal'].sum()}, Suboptimal: {(~df['is_optimal'].astype(bool)).sum()}")
        
        return df
    
    def train(self, df: pd.DataFrame = None) -> dict:
        """
        Train Random Forest model.
        
        Args:
            df: Training DataFrame (if None, generates synthetic data)
            
        Returns:
            Dictionary with training metrics
        """
        if df is None:
            df = self.generate_synthetic_data()
        
        # Prepare features and labels
        X = df[self.feature_names].values
        y = df['is_optimal'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest
        logger.info("Training Random Forest classifier...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.random_state,
            n_jobs=-1,
            class_weight='balanced'  # Handle class imbalance
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        logger.info("\n" + "="*50)
        logger.info("Model Performance Metrics:")
        logger.info(f"Accuracy:  {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall:    {recall:.4f}")
        logger.info(f"F1 Score:  {f1:.4f}")
        logger.info("="*50)
        
        logger.info("\nClassification Report:")
        logger.info("\n" + classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        logger.info("\nTop 5 Most Important Features:")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {feature}: {importance:.4f}")
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'feature_importance': feature_importance,
            'n_samples': len(df),
            'n_train': len(X_train),
            'n_test': len(X_test),
        }
        
        return metrics
    
    def save_model(self, output_path: str):
        """
        Save trained model to disk.
        
        Args:
            output_path: Path to save model file
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info(f"Model saved to {output_path}")
        
        # Also save feature names for reference
        feature_info_path = output_path.replace('.pkl', '_features.txt')
        with open(feature_info_path, 'w') as f:
            f.write('\n'.join(self.feature_names))
        
        logger.info(f"Feature names saved to {feature_info_path}")


def main():
    """Main training function."""
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(script_dir, '../models')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'rf_model.pkl')
    
    logger.info("="*60)
    logger.info("ASLPS Model Training")
    logger.info("="*60)
    
    # Initialize trainer
    trainer = ModelTrainer(n_samples=5000, random_state=42)
    
    # Train model
    metrics = trainer.train()
    
    # Save model
    trainer.save_model(model_path)
    
    logger.info("\n" + "="*60)
    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_path}")
    logger.info("="*60)
    
    return metrics


if __name__ == '__main__':
    main()

