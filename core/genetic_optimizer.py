# core/genetic_optimizer.py
# -*- coding: utf-8 -*-
"""
Genetik Optimizator (Evolyutsiya Dvigateli).

Bu modul "Sun'iy Ong"ning asosiy dvigatelidir. U minglab xil variantlarni
yaratadi, ularni baholaydi va vaqt o'tishi bilan eng mukammal uy planirovkasiga
o'xshab boradi.
"""

import time
import random
import logging
from typing import List, Dict, Callable, Tuple, Any
from concurrent.futures import ProcessPoolExecutor, as_completed

from core.models import (
    RoomRequest, HouseGenome, HousePlan, OptimizationResult
)
from core.genome import (
    create_random_house_genome, mutate_floor_genome, crossover_house_genomes
)
from config.settings import (
    GA_POPULATION_SIZE, GA_GENERATIONS, GA_ELITE_COUNT, 
    GA_TOURNAMENT_SIZE, GA_MUTATION_RATE, GA_CROSSOVER_RATE,
    GA_RANDOM_IMMIGRANTS, GA_STAGNATION_LIMIT, GA_DEFAULT_SEED
)

logger = logging.getLogger(__name__)

# Baholovchi funksiya turi: Genomni oladi, (Ball, Tahlil, Uy_Rejasi) qaytaradi
FitnessEvaluator = Callable[[HouseGenome], Tuple[float, Dict[str, float], HousePlan]]


class GeneticOptimizer:
    """
    Uy planirovkasini yaratish uchun genetik algoritmni ishga tushiruvchi sinf.
    """

    def __init__(
        self,
        population_size: int = GA_POPULATION_SIZE,
        generations: int = GA_GENERATIONS,
        mutation_rate: float = GA_MUTATION_RATE,
        crossover_rate: float = GA_CROSSOVER_RATE,
        elite_count: int = GA_ELITE_COUNT,
        tournament_size: int = GA_TOURNAMENT_SIZE,
        stagnation_limit: int = GA_STAGNATION_LIMIT,
        seed: int = GA_DEFAULT_SEED
    ):
        self.pop_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_count = elite_count
        self.tournament_size = tournament_size
        self.stagnation_limit = stagnation_limit
        self.rng = random.Random(seed)

    def _tournament_selection(self, evaluated_population: List[Tuple[float, HouseGenome, HousePlan]]) -> HouseGenome:
        """Turnir usulida ota-onani tanlash (eng yaxshilarga ko'proq imkoniyat)."""
        tournament = self.rng.sample(evaluated_population, self.tournament_size)
        tournament.sort(key=lambda x: x[0], reverse=True)
        return tournament[0][1] # Eng yaxshi genomni qaytarish

    def optimize(
        self,
        requests: List[RoomRequest],
        floor_count: int,
        evaluator: FitnessEvaluator
    ) -> OptimizationResult:
        """
        Asosiy evolyutsiya jarayoni.
        """
        start_time = time.time()
        
        # 1. Boshlang'ich populyatsiyani yaratish
        population = [
            create_random_house_genome(requests, floor_count, self.rng) 
            for _ in range(self.pop_size)
        ]

        best_overall_score = -1.0
        best_overall_genome = None
        best_overall_house = None
        stagnation_counter = 0
        
        history = []
        mean_history = []

        logger.info(f"AI qidiruvi boshlandi. Populyatsiya: {self.pop_size}, Avlodlar: {self.generations}")

        for gen in range(self.generations):
            evaluated_population = []
            
            # Har bir genomni baholash
            for genome in population:
                try:
                    score, breakdown, house_plan = evaluator(genome)
                    evaluated_population.append((score, genome, house_plan))
                except Exception as e:
                    logger.error(f"Genomni baholashda xato: {e}")
                    evaluated_population.append((0.0, genome, None))

            # Saralash (eng yuqori ball birinchi)
            evaluated_population.sort(key=lambda x: x[0], reverse=True)
            
            # Statistikani yig'ish
            current_best_score = evaluated_population[0][0]
            current_mean_score = sum(x[0] for x in evaluated_population) / len(evaluated_population)
            history.append(current_best_score)
            mean_history.append(current_mean_score)

            # Eng yaxshisini saqlab qolish
            if current_best_score > best_overall_score:
                best_overall_score = current_best_score
                best_overall_genome = evaluated_population[0][1].copy()
                best_overall_house = evaluated_population[0][2]
                stagnation_counter = 0
            else:
                stagnation_counter += 1

            # To'xtash sharti (agar ball o'sishdan to'xtasa)
            if stagnation_counter >= self.stagnation_limit:
                logger.info(f"Stagnatsiya aniqlandi. {gen}-avloddan keyin to'xtatildi.")
                break

            # --- KEYINGI AVLODNI YARATISH ---
            next_population = []
            
            # 1. Elitizm (eng yaxshi genlarni saqlab qolish)
            for i in range(self.elite_count):
                next_population.append(evaluated_population[i][1].copy())

            # 2. Krossover va Mutatsiya
            while len(next_population) < self.pop_size - GA_RANDOM_IMMIGRANTS:
                parent1 = self._tournament_selection(evaluated_population)
                parent2 = self._tournament_selection(evaluated_population)
                
                if self.rng.random() < self.crossover_rate:
                    child1, child2 = crossover_house_genomes(parent1, parent2, self.rng)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutatsiya qo'llash
                for f_idx in range(len(child1.floor_genomes)):
                    child1.floor_genomes[f_idx] = mutate_floor_genome(
                        child1.floor_genomes[f_idx], requests, self.rng, self.mutation_rate
                    )
                for f_idx in range(len(child2.floor_genomes)):
                    child2.floor_genomes[f_idx] = mutate_floor_genome(
                        child2.floor_genomes[f_idx], requests, self.rng, self.mutation_rate
                    )
                
                next_population.append(child1)
                if len(next_population) < self.pop_size - GA_RANDOM_IMMIGRANTS:
                    next_population.append(child2)

            # 3. Tasodifiy yangi genlar (Immigratsiya - xilma-xillik uchun)
            for _ in range(GA_RANDOM_IMMIGRANTS):
                next_population.append(create_random_house_genome(requests, floor_count, self.rng))

            population = next_population

        elapsed = time.time() - start_time
        logger.info(f"AI qidiruvi tugadi. Eng yaxshi ball: {best_overall_score:.1f} / 100. {elapsed:.2f} soniya.")

        return OptimizationResult(
            best_genome=best_overall_genome,
            best_house=best_overall_house,
            best_score=best_overall_score,
            all_time_best_score=best_overall_score,
            history=history,
            mean_history=mean_history,
            generations_run=gen + 1,
            stagnation_reached=(stagnation_counter >= self.stagnation_limit),
            elapsed_seconds=elapsed,
            population_size=self.pop_size
        )
