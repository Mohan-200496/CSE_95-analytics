"""
Genetic Algorithm for Profile-Job Matching
Optimizes job recommendations based on candidate profiles and job requirements
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    """Candidate profile for GA optimization"""
    user_id: str
    skills: List[str]
    experience_years: int
    education_level: str
    preferred_locations: List[str]
    preferred_job_types: List[str]
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None


@dataclass
class JobProfile:
    """Job profile for GA optimization"""
    job_id: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_min: int
    experience_max: Optional[int]
    education_level: str
    location_city: str
    job_type: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    category: str = ""


@dataclass
class MatchingGene:
    """Individual gene in the GA population representing a job-candidate match"""
    job_id: str
    candidate_id: str
    fitness_score: float = 0.0
    skill_match_score: float = 0.0
    experience_match_score: float = 0.0
    location_match_score: float = 0.0
    salary_match_score: float = 0.0
    education_match_score: float = 0.0


class GeneticJobMatcher:
    """
    Genetic Algorithm implementation for optimizing job-candidate matching
    Treats job matching as an optimization problem
    """
    
    def __init__(
        self,
        population_size: int = 100,
        generations: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_percentage: float = 0.2
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_count = int(population_size * elite_percentage)
        
        # Fitness weights for different matching criteria
        self.weights = {
            'skills': 0.35,
            'experience': 0.25,
            'location': 0.15,
            'salary': 0.15,
            'education': 0.10
        }
    
    def calculate_skill_match(self, candidate: Candidate, job: JobProfile) -> float:
        """Calculate skill matching score using Jaccard similarity"""
        if not job.required_skills and not job.preferred_skills:
            return 0.5  # Neutral score if no skills specified
        
        candidate_skills = set(skill.lower().strip() for skill in candidate.skills)
        required_skills = set(skill.lower().strip() for skill in job.required_skills)
        preferred_skills = set(skill.lower().strip() for skill in job.preferred_skills)
        
        # Required skills matching (weighted more heavily)
        required_intersection = len(candidate_skills.intersection(required_skills))
        required_union = len(candidate_skills.union(required_skills))
        required_score = required_intersection / max(required_union, 1)
        
        # Preferred skills matching
        preferred_intersection = len(candidate_skills.intersection(preferred_skills))
        preferred_union = len(candidate_skills.union(preferred_skills))
        preferred_score = preferred_intersection / max(preferred_union, 1) if preferred_skills else 0
        
        # Combined score (required skills weighted 70%, preferred 30%)
        combined_score = (required_score * 0.7) + (preferred_score * 0.3)
        return min(combined_score, 1.0)
    
    def calculate_experience_match(self, candidate: Candidate, job: JobProfile) -> float:
        """Calculate experience matching score"""
        candidate_exp = candidate.experience_years
        min_exp = job.experience_min
        max_exp = job.experience_max or float('inf')
        
        if candidate_exp < min_exp:
            # Penalize under-qualified candidates
            gap = min_exp - candidate_exp
            return max(0.0, 1.0 - (gap * 0.2))
        elif max_exp != float('inf') and candidate_exp > max_exp:
            # Slight penalty for over-qualified candidates
            excess = candidate_exp - max_exp
            return max(0.7, 1.0 - (excess * 0.1))
        else:
            # Perfect match within range
            return 1.0
    
    def calculate_location_match(self, candidate: Candidate, job: JobProfile) -> float:
        """Calculate location matching score"""
        if not candidate.preferred_locations:
            return 0.5  # Neutral score if no preference
        
        job_location = job.location_city.lower().strip()
        for preferred_location in candidate.preferred_locations:
            if preferred_location.lower().strip() in job_location or job_location in preferred_location.lower().strip():
                return 1.0
        
        return 0.2  # Low score if location doesn't match
    
    def calculate_salary_match(self, candidate: Candidate, job: JobProfile) -> float:
        """Calculate salary matching score"""
        if not candidate.expected_salary_min and not candidate.expected_salary_max:
            return 0.5  # Neutral if no salary expectation
        
        if not job.salary_min and not job.salary_max:
            return 0.5  # Neutral if job salary not specified
        
        candidate_min = candidate.expected_salary_min or 0
        candidate_max = candidate.expected_salary_max or float('inf')
        job_min = job.salary_min or 0
        job_max = job.salary_max or float('inf')
        
        # Check for overlap between salary ranges
        overlap_min = max(candidate_min, job_min)
        overlap_max = min(candidate_max, job_max)
        
        if overlap_min <= overlap_max:
            # Calculate overlap percentage
            candidate_range = candidate_max - candidate_min if candidate_max != float('inf') else job_max - candidate_min
            job_range = job_max - job_min if job_max != float('inf') else candidate_max - job_min
            overlap_range = overlap_max - overlap_min
            
            if candidate_range > 0 and job_range > 0:
                overlap_score = overlap_range / min(candidate_range, job_range)
                return min(overlap_score, 1.0)
            else:
                return 1.0
        else:
            # No overlap - calculate penalty based on gap
            gap = min(abs(candidate_min - job_max), abs(job_min - candidate_max))
            avg_salary = (candidate_min + job_min) / 2
            gap_percentage = gap / max(avg_salary, 1)
            return max(0.0, 1.0 - gap_percentage)
    
    def calculate_education_match(self, candidate: Candidate, job: JobProfile) -> float:
        """Calculate education level matching score"""
        education_hierarchy = {
            'high_school': 1, 'high-school': 1,
            'diploma': 2,
            'bachelors': 3, "bachelor's": 3, 'bachelor': 3,
            'masters': 4, "master's": 4, 'master': 4,
            'phd': 5, 'doctorate': 5
        }
        
        candidate_level = education_hierarchy.get(candidate.education_level.lower(), 3)
        job_level = education_hierarchy.get(job.education_level.lower(), 3)
        
        if candidate_level >= job_level:
            return 1.0  # Meets or exceeds requirements
        else:
            # Penalty for not meeting education requirements
            gap = job_level - candidate_level
            return max(0.3, 1.0 - (gap * 0.2))
    
    def calculate_fitness(self, candidate: Candidate, job: JobProfile) -> MatchingGene:
        """Calculate overall fitness score for a candidate-job pair"""
        skill_score = self.calculate_skill_match(candidate, job)
        experience_score = self.calculate_experience_match(candidate, job)
        location_score = self.calculate_location_match(candidate, job)
        salary_score = self.calculate_salary_match(candidate, job)
        education_score = self.calculate_education_match(candidate, job)
        
        # Weighted fitness score
        fitness_score = (
            skill_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            location_score * self.weights['location'] +
            salary_score * self.weights['salary'] +
            education_score * self.weights['education']
        )
        
        return MatchingGene(
            job_id=job.job_id,
            candidate_id=candidate.user_id,
            fitness_score=fitness_score,
            skill_match_score=skill_score,
            experience_match_score=experience_score,
            location_match_score=location_score,
            salary_match_score=salary_score,
            education_match_score=education_score
        )
    
    def create_initial_population(
        self, 
        candidate: Candidate, 
        jobs: List[JobProfile]
    ) -> List[MatchingGene]:
        """Create initial population of candidate-job matches"""
        population = []
        
        for job in jobs:
            gene = self.calculate_fitness(candidate, job)
            population.append(gene)
        
        # If we have fewer jobs than desired population size, duplicate with mutations
        while len(population) < self.population_size and jobs:
            job = random.choice(jobs)
            gene = self.calculate_fitness(candidate, job)
            # Add some randomness to create diversity
            gene.fitness_score += random.uniform(-0.1, 0.1)
            gene.fitness_score = max(0.0, min(1.0, gene.fitness_score))
            population.append(gene)
        
        return population[:self.population_size]
    
    def selection(self, population: List[MatchingGene]) -> List[MatchingGene]:
        """Tournament selection for breeding"""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x.fitness_score)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1: MatchingGene, parent2: MatchingGene) -> Tuple[MatchingGene, MatchingGene]:
        """Single-point crossover between two matching genes"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # Create offspring by averaging fitness components
        child1 = MatchingGene(
            job_id=parent1.job_id,
            candidate_id=parent1.candidate_id,
            skill_match_score=(parent1.skill_match_score + parent2.skill_match_score) / 2,
            experience_match_score=(parent1.experience_match_score + parent2.experience_match_score) / 2,
            location_match_score=(parent1.location_match_score + parent2.location_match_score) / 2,
            salary_match_score=(parent1.salary_match_score + parent2.salary_match_score) / 2,
            education_match_score=(parent1.education_match_score + parent2.education_match_score) / 2
        )
        
        child2 = MatchingGene(
            job_id=parent2.job_id,
            candidate_id=parent2.candidate_id,
            skill_match_score=(parent1.skill_match_score + parent2.skill_match_score) / 2,
            experience_match_score=(parent1.experience_match_score + parent2.experience_match_score) / 2,
            location_match_score=(parent1.location_match_score + parent2.location_match_score) / 2,
            salary_match_score=(parent1.salary_match_score + parent2.salary_match_score) / 2,
            education_match_score=(parent1.education_match_score + parent2.education_match_score) / 2
        )
        
        # Recalculate fitness scores
        child1.fitness_score = (
            child1.skill_match_score * self.weights['skills'] +
            child1.experience_match_score * self.weights['experience'] +
            child1.location_match_score * self.weights['location'] +
            child1.salary_match_score * self.weights['salary'] +
            child1.education_match_score * self.weights['education']
        )
        
        child2.fitness_score = (
            child2.skill_match_score * self.weights['skills'] +
            child2.experience_match_score * self.weights['experience'] +
            child2.location_match_score * self.weights['location'] +
            child2.salary_match_score * self.weights['salary'] +
            child2.education_match_score * self.weights['education']
        )
        
        return child1, child2
    
    def mutate(self, gene: MatchingGene) -> MatchingGene:
        """Mutate a matching gene by adding random noise"""
        if random.random() > self.mutation_rate:
            return gene
        
        # Add small random changes to fitness components
        mutation_strength = 0.05
        gene.skill_match_score = max(0.0, min(1.0, 
            gene.skill_match_score + random.uniform(-mutation_strength, mutation_strength)))
        gene.experience_match_score = max(0.0, min(1.0,
            gene.experience_match_score + random.uniform(-mutation_strength, mutation_strength)))
        gene.location_match_score = max(0.0, min(1.0,
            gene.location_match_score + random.uniform(-mutation_strength, mutation_strength)))
        gene.salary_match_score = max(0.0, min(1.0,
            gene.salary_match_score + random.uniform(-mutation_strength, mutation_strength)))
        gene.education_match_score = max(0.0, min(1.0,
            gene.education_match_score + random.uniform(-mutation_strength, mutation_strength)))
        
        # Recalculate fitness score
        gene.fitness_score = (
            gene.skill_match_score * self.weights['skills'] +
            gene.experience_match_score * self.weights['experience'] +
            gene.location_match_score * self.weights['location'] +
            gene.salary_match_score * self.weights['salary'] +
            gene.education_match_score * self.weights['education']
        )
        
        return gene
    
    def evolve_population(
        self, 
        candidate: Candidate, 
        jobs: List[JobProfile],
        max_recommendations: int = 10
    ) -> List[MatchingGene]:
        """
        Main GA evolution process to find optimal job matches
        
        Args:
            candidate: Candidate profile to match
            jobs: List of available jobs
            max_recommendations: Maximum number of job recommendations to return
            
        Returns:
            List of top matching genes sorted by fitness score
        """
        if not jobs:
            return []
        
        # Create initial population
        population = self.create_initial_population(candidate, jobs)
        
        # Evolution loop
        for generation in range(self.generations):
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            # Elite preservation
            next_population = population[:self.elite_count]
            
            # Generate offspring to fill the rest of the population
            while len(next_population) < self.population_size:
                # Selection
                selected = self.selection(population)
                
                # Crossover
                for i in range(0, len(selected) - 1, 2):
                    if len(next_population) >= self.population_size:
                        break
                    
                    parent1, parent2 = selected[i], selected[i + 1]
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    # Mutation
                    child1 = self.mutate(child1)
                    child2 = self.mutate(child2)
                    
                    next_population.extend([child1, child2])
            
            population = next_population[:self.population_size]
            
            # Log progress every 10 generations
            if generation % 10 == 0:
                best_fitness = max(gene.fitness_score for gene in population)
                logger.debug(f"Generation {generation}: Best fitness = {best_fitness:.3f}")
        
        # Final sorting and return top recommendations
        population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Remove duplicates and return top matches
        seen_jobs = set()
        unique_matches = []
        
        for gene in population:
            if gene.job_id not in seen_jobs:
                seen_jobs.add(gene.job_id)
                unique_matches.append(gene)
                
                if len(unique_matches) >= max_recommendations:
                    break
        
        return unique_matches
    
    async def get_job_recommendations(
        self, 
        candidate: Candidate, 
        jobs: List[JobProfile],
        max_recommendations: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get job recommendations for a candidate using GA optimization
        
        Returns:
            List of job recommendations with detailed matching scores
        """
        try:
            # Run GA optimization
            matches = self.evolve_population(candidate, jobs, max_recommendations)
            
            # Format results
            recommendations = []
            for match in matches:
                recommendation = {
                    'job_id': match.job_id,
                    'candidate_id': match.candidate_id,
                    'overall_score': round(match.fitness_score, 3),
                    'match_breakdown': {
                        'skills': round(match.skill_match_score, 3),
                        'experience': round(match.experience_match_score, 3),
                        'location': round(match.location_match_score, 3),
                        'salary': round(match.salary_match_score, 3),
                        'education': round(match.education_match_score, 3)
                    },
                    'recommendation_source': 'genetic_algorithm',
                    'generated_at': datetime.utcnow().isoformat()
                }
                recommendations.append(recommendation)
            
            logger.info(f"Generated {len(recommendations)} GA recommendations for candidate {candidate.user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in GA job recommendations: {str(e)}")
            return []


# Global GA matcher instance
ga_matcher = GeneticJobMatcher()


async def get_ga_recommendations(
    candidate: Candidate, 
    jobs: List[JobProfile], 
    max_recommendations: int = 10
) -> List[Dict[str, any]]:
    """Convenience function to get GA-based recommendations"""
    return await ga_matcher.get_job_recommendations(candidate, jobs, max_recommendations)