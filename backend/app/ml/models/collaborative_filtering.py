"""
Collaborative Filtering for Behavior-Based Job Recommendations
Learns from collective user behavior to discover relevant jobs
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class UserInteraction:
    """User interaction data for collaborative filtering"""
    user_id: str
    job_id: str
    interaction_type: str  # 'view', 'click', 'apply', 'save'
    timestamp: datetime
    interaction_value: float = 1.0  # Weight of interaction


@dataclass
class UserProfile:
    """User profile for CF analysis"""
    user_id: str
    interactions: List[UserInteraction]
    skills: List[str]
    job_category_preferences: List[str]
    location_preferences: List[str]
    activity_score: float = 0.0


class CollaborativeFilter:
    """
    Collaborative Filtering implementation for job recommendations
    Uses both user-based and item-based filtering with matrix factorization
    """
    
    def __init__(
        self,
        min_interactions: int = 5,
        similarity_threshold: float = 0.1,
        max_recommendations: int = 50,
        interaction_weights: Dict[str, float] = None
    ):
        self.min_interactions = min_interactions
        self.similarity_threshold = similarity_threshold
        self.max_recommendations = max_recommendations
        
        # Default interaction weights
        self.interaction_weights = interaction_weights or {
            'view': 1.0,
            'click': 2.0,
            'save': 3.0,
            'apply': 5.0,
            'shortlist': 4.0
        }
        
        # Internal matrices
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_index_map = {}
        self.item_index_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
        
        # Matrix factorization model
        self.svd_model = None
        self.reduced_matrix = None
        
        # Cache for performance
        self.recommendation_cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(hours=6)
    
    def _apply_time_decay(self, interactions: List[UserInteraction]) -> List[UserInteraction]:
        """Apply time decay to interactions (more recent = higher weight)"""
        now = datetime.utcnow()
        decayed_interactions = []
        
        for interaction in interactions:
            # Calculate days since interaction
            days_ago = (now - interaction.timestamp).days
            
            # Apply exponential decay (half-life of 30 days)
            decay_factor = np.exp(-days_ago / 30.0)
            
            # Update interaction value
            decayed_interaction = UserInteraction(
                user_id=interaction.user_id,
                job_id=interaction.job_id,
                interaction_type=interaction.interaction_type,
                timestamp=interaction.timestamp,
                interaction_value=interaction.interaction_value * decay_factor
            )
            decayed_interactions.append(decayed_interaction)
        
        return decayed_interactions
    
    def _build_user_item_matrix(self, interactions: List[UserInteraction]) -> csr_matrix:
        """Build user-item interaction matrix"""
        # Apply time decay
        decayed_interactions = self._apply_time_decay(interactions)
        
        # Group interactions by user-item pairs
        interaction_dict = defaultdict(float)
        users = set()
        items = set()
        
        for interaction in decayed_interactions:
            users.add(interaction.user_id)
            items.add(interaction.job_id)
            
            # Apply interaction type weight
            weight = self.interaction_weights.get(interaction.interaction_type, 1.0)
            weighted_value = interaction.interaction_value * weight
            
            # Accumulate interactions for same user-item pair
            interaction_dict[(interaction.user_id, interaction.job_id)] += weighted_value
        
        # Create index mappings
        users = sorted(list(users))
        items = sorted(list(items))
        
        self.user_index_map = {user: idx for idx, user in enumerate(users)}
        self.item_index_map = {item: idx for idx, item in enumerate(items)}
        self.reverse_user_map = {idx: user for user, idx in self.user_index_map.items()}
        self.reverse_item_map = {idx: item for item, idx in self.item_index_map.items()}
        
        # Build sparse matrix
        n_users = len(users)
        n_items = len(items)
        
        row_indices = []
        col_indices = []
        data = []
        
        for (user_id, item_id), value in interaction_dict.items():
            if user_id in self.user_index_map and item_id in self.item_index_map:
                row_indices.append(self.user_index_map[user_id])
                col_indices.append(self.item_index_map[item_id])
                data.append(value)
        
        matrix = csr_matrix((data, (row_indices, col_indices)), shape=(n_users, n_items))
        
        logger.info(f"Built user-item matrix: {n_users} users, {n_items} items, {matrix.nnz} interactions")
        return matrix
    
    def _compute_user_similarity(self) -> np.ndarray:
        """Compute user-user similarity matrix using cosine similarity"""
        # Normalize the matrix for better similarity computation
        normalized_matrix = self.user_item_matrix.copy().astype(float)
        
        # Convert to dense for sklearn (handle memory efficiently)
        if normalized_matrix.shape[0] > 1000:
            # Use sampling for very large matrices
            sample_size = 1000
            sample_indices = np.random.choice(
                normalized_matrix.shape[0], 
                min(sample_size, normalized_matrix.shape[0]), 
                replace=False
            )
            sample_matrix = normalized_matrix[sample_indices].toarray()
            similarity_matrix = cosine_similarity(sample_matrix)
            
            # Expand back to full size with zeros
            full_similarity = np.zeros((normalized_matrix.shape[0], normalized_matrix.shape[0]))
            for i, idx_i in enumerate(sample_indices):
                for j, idx_j in enumerate(sample_indices):
                    full_similarity[idx_i, idx_j] = similarity_matrix[i, j]
            
            return full_similarity
        else:
            # Compute full similarity matrix
            dense_matrix = normalized_matrix.toarray()
            return cosine_similarity(dense_matrix)
    
    def _compute_item_similarity(self) -> np.ndarray:
        """Compute item-item similarity matrix"""
        # Transpose for item-based similarity
        item_matrix = self.user_item_matrix.T
        
        if item_matrix.shape[0] > 2000:
            # Use sampling for large item spaces
            sample_size = 2000
            sample_indices = np.random.choice(
                item_matrix.shape[0], 
                min(sample_size, item_matrix.shape[0]), 
                replace=False
            )
            sample_matrix = item_matrix[sample_indices].toarray()
            similarity_matrix = cosine_similarity(sample_matrix)
            
            # Expand back to full size
            full_similarity = np.zeros((item_matrix.shape[0], item_matrix.shape[0]))
            for i, idx_i in enumerate(sample_indices):
                for j, idx_j in enumerate(sample_indices):
                    full_similarity[idx_i, idx_j] = similarity_matrix[i, j]
            
            return full_similarity
        else:
            dense_matrix = item_matrix.toarray()
            return cosine_similarity(dense_matrix)
    
    def _matrix_factorization(self, n_components: int = 50) -> np.ndarray:
        """Apply matrix factorization using SVD"""
        try:
            self.svd_model = TruncatedSVD(
                n_components=min(n_components, min(self.user_item_matrix.shape) - 1),
                random_state=42
            )
            self.reduced_matrix = self.svd_model.fit_transform(self.user_item_matrix)
            
            logger.info(f"Matrix factorization completed: {self.reduced_matrix.shape}")
            return self.reduced_matrix
        except Exception as e:
            logger.error(f"Matrix factorization failed: {str(e)}")
            return None
    
    def fit(self, interactions: List[UserInteraction]) -> None:
        """Fit the collaborative filtering model"""
        logger.info(f"Fitting CF model with {len(interactions)} interactions")
        
        # Build user-item matrix
        self.user_item_matrix = self._build_user_item_matrix(interactions)
        
        if self.user_item_matrix.nnz < self.min_interactions:
            logger.warning(f"Insufficient interactions ({self.user_item_matrix.nnz}) for CF model")
            return
        
        # Compute similarity matrices
        try:
            self.user_similarity_matrix = self._compute_user_similarity()
            self.item_similarity_matrix = self._compute_item_similarity()
            
            # Apply matrix factorization
            self._matrix_factorization()
            
            logger.info("CF model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting CF model: {str(e)}")
    
    def _get_user_based_recommendations(
        self, 
        user_id: str, 
        n_recommendations: int = 10
    ) -> List[Tuple[str, float]]:
        """Get recommendations using user-based collaborative filtering"""
        if user_id not in self.user_index_map:
            return []
        
        user_idx = self.user_index_map[user_id]
        user_similarities = self.user_similarity_matrix[user_idx]
        
        # Find similar users
        similar_user_indices = np.argsort(user_similarities)[::-1][1:21]  # Top 20 similar users
        similar_users = [
            (self.reverse_user_map[idx], user_similarities[idx]) 
            for idx in similar_user_indices 
            if user_similarities[idx] > self.similarity_threshold
        ]
        
        if not similar_users:
            return []
        
        # Get items that similar users liked but current user hasn't interacted with
        user_items = set(self.user_item_matrix[user_idx].nonzero()[1])
        recommendations = defaultdict(float)
        
        for similar_user_id, similarity in similar_users:
            if similar_user_id in self.user_index_map:
                similar_user_idx = self.user_index_map[similar_user_id]
                similar_user_items = self.user_item_matrix[similar_user_idx].nonzero()[1]
                
                for item_idx in similar_user_items:
                    if item_idx not in user_items:
                        item_id = self.reverse_item_map[item_idx]
                        interaction_score = self.user_item_matrix[similar_user_idx, item_idx]
                        recommendations[item_id] += similarity * interaction_score
        
        # Sort and return top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]
    
    def _get_item_based_recommendations(
        self, 
        user_id: str, 
        n_recommendations: int = 10
    ) -> List[Tuple[str, float]]:
        """Get recommendations using item-based collaborative filtering"""
        if user_id not in self.user_index_map:
            return []
        
        user_idx = self.user_index_map[user_id]
        user_items = self.user_item_matrix[user_idx].nonzero()[1]
        
        if len(user_items) == 0:
            return []
        
        # Get recommendations based on similar items
        recommendations = defaultdict(float)
        
        for item_idx in user_items:
            item_similarities = self.item_similarity_matrix[item_idx]
            user_rating = self.user_item_matrix[user_idx, item_idx]
            
            # Find similar items
            similar_items = np.argsort(item_similarities)[::-1][1:11]  # Top 10 similar items
            
            for similar_item_idx in similar_items:
                if (similar_item_idx not in user_items and 
                    item_similarities[similar_item_idx] > self.similarity_threshold):
                    
                    similar_item_id = self.reverse_item_map[similar_item_idx]
                    score = item_similarities[similar_item_idx] * user_rating
                    recommendations[similar_item_id] += score
        
        # Sort and return top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]
    
    def _get_matrix_factorization_recommendations(
        self, 
        user_id: str, 
        n_recommendations: int = 10
    ) -> List[Tuple[str, float]]:
        """Get recommendations using matrix factorization"""
        if (self.svd_model is None or self.reduced_matrix is None or 
            user_id not in self.user_index_map):
            return []
        
        user_idx = self.user_index_map[user_id]
        user_vector = self.reduced_matrix[user_idx]
        
        # Reconstruct full ratings for this user
        item_factors = self.svd_model.components_
        predicted_ratings = np.dot(user_vector, item_factors)
        
        # Get items user hasn't interacted with
        user_items = set(self.user_item_matrix[user_idx].nonzero()[1])
        
        recommendations = []
        for item_idx, score in enumerate(predicted_ratings):
            if item_idx not in user_items:
                item_id = self.reverse_item_map[item_idx]
                recommendations.append((item_id, score))
        
        # Sort and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def get_recommendations(
        self, 
        user_id: str, 
        n_recommendations: int = 10,
        method: str = 'hybrid'
    ) -> List[Dict[str, any]]:
        """
        Get job recommendations using collaborative filtering
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            method: 'user_based', 'item_based', 'matrix_factorization', or 'hybrid'
            
        Returns:
            List of job recommendations with scores
        """
        # Check cache first
        cache_key = f"{user_id}_{n_recommendations}_{method}"
        if (cache_key in self.recommendation_cache and 
            self.cache_expiry.get(cache_key, datetime.min) > datetime.utcnow()):
            return self.recommendation_cache[cache_key]
        
        try:
            if method == 'user_based':
                recommendations = self._get_user_based_recommendations(user_id, n_recommendations)
            elif method == 'item_based':
                recommendations = self._get_item_based_recommendations(user_id, n_recommendations)
            elif method == 'matrix_factorization':
                recommendations = self._get_matrix_factorization_recommendations(user_id, n_recommendations)
            else:  # hybrid
                # Combine all three methods
                user_recs = self._get_user_based_recommendations(user_id, n_recommendations)
                item_recs = self._get_item_based_recommendations(user_id, n_recommendations)
                mf_recs = self._get_matrix_factorization_recommendations(user_id, n_recommendations)
                
                # Weighted combination
                combined_scores = defaultdict(float)
                weights = {'user': 0.4, 'item': 0.3, 'mf': 0.3}
                
                for job_id, score in user_recs:
                    combined_scores[job_id] += score * weights['user']
                
                for job_id, score in item_recs:
                    combined_scores[job_id] += score * weights['item']
                
                for job_id, score in mf_recs:
                    combined_scores[job_id] += score * weights['mf']
                
                recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
                recommendations = recommendations[:n_recommendations]
            
            # Format results
            formatted_recommendations = []
            for job_id, score in recommendations:
                recommendation = {
                    'job_id': job_id,
                    'user_id': user_id,
                    'cf_score': round(float(score), 3),
                    'recommendation_source': f'collaborative_filtering_{method}',
                    'generated_at': datetime.utcnow().isoformat()
                }
                formatted_recommendations.append(recommendation)
            
            # Cache results
            self.recommendation_cache[cache_key] = formatted_recommendations
            self.cache_expiry[cache_key] = datetime.utcnow() + self.cache_duration
            
            logger.info(f"Generated {len(formatted_recommendations)} CF recommendations for user {user_id}")
            return formatted_recommendations
            
        except Exception as e:
            logger.error(f"Error generating CF recommendations for user {user_id}: {str(e)}")
            return []
    
    def get_user_similarity(self, user_id1: str, user_id2: str) -> float:
        """Get similarity score between two users"""
        if (user_id1 not in self.user_index_map or 
            user_id2 not in self.user_index_map or
            self.user_similarity_matrix is None):
            return 0.0
        
        idx1 = self.user_index_map[user_id1]
        idx2 = self.user_index_map[user_id2]
        
        return float(self.user_similarity_matrix[idx1, idx2])
    
    def get_item_similarity(self, job_id1: str, job_id2: str) -> float:
        """Get similarity score between two jobs"""
        if (job_id1 not in self.item_index_map or 
            job_id2 not in self.item_index_map or
            self.item_similarity_matrix is None):
            return 0.0
        
        idx1 = self.item_index_map[job_id1]
        idx2 = self.item_index_map[job_id2]
        
        return float(self.item_similarity_matrix[idx1, idx2])
    
    def clear_cache(self) -> None:
        """Clear recommendation cache"""
        self.recommendation_cache.clear()
        self.cache_expiry.clear()
        logger.info("CF recommendation cache cleared")


# Global CF instance
cf_model = CollaborativeFilter()


async def fit_collaborative_filter(interactions: List[UserInteraction]) -> None:
    """Fit the collaborative filtering model asynchronously"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, cf_model.fit, interactions)


async def get_cf_recommendations(
    user_id: str, 
    n_recommendations: int = 10,
    method: str = 'hybrid'
) -> List[Dict[str, any]]:
    """Get collaborative filtering recommendations asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        cf_model.get_recommendations, 
        user_id, 
        n_recommendations, 
        method
    )