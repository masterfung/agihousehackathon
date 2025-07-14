"""
Restaurant evaluator module - scores restaurants based on user preferences
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
try:
    from .preferences import UserContext
except ImportError:
    from preferences import UserContext


@dataclass
class RestaurantInfo:
    """Information about a restaurant extracted from web sources"""
    name: str
    cuisine_type: List[str]
    price_range: str  # $, $$, $$$, $$$$
    address: str
    distance_miles: Optional[float] = None
    has_vegetarian_menu: Optional[bool] = None
    vegetarian_options_count: int = 0
    menu_items: List[str] = None
    wine_list_quality: Optional[str] = None  # basic, good, excellent
    allows_corkage: Optional[bool] = None
    near_public_transit: Optional[bool] = None
    reviews_summary: Optional[str] = None
    rating: Optional[float] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        if self.menu_items is None:
            self.menu_items = []


@dataclass
class EvaluationScore:
    """Detailed scoring breakdown for a restaurant"""
    total_score: float  # 0-100
    dietary_score: float  # 0-25
    cuisine_score: float  # 0-20
    budget_score: float  # 0-20
    location_score: float  # 0-20
    wine_score: float  # 0-15
    explanation: str
    match_reasons: List[str]
    concerns: List[str]


class RestaurantEvaluator:
    """Evaluates restaurants based on user preferences"""
    
    def __init__(self, user_context: UserContext):
        self.context = user_context
        
    def evaluate_restaurant(self, restaurant: RestaurantInfo) -> EvaluationScore:
        """
        Score a restaurant based on how well it matches user preferences
        Returns a score from 0-100 with detailed breakdown
        """
        dietary_score = self._score_dietary_fit(restaurant)
        cuisine_score = self._score_cuisine_fit(restaurant)
        budget_score = self._score_budget_fit(restaurant)
        location_score = self._score_location_fit(restaurant)
        wine_score = self._score_wine_fit(restaurant)
        
        total_score = (
            dietary_score + 
            cuisine_score + 
            budget_score + 
            location_score + 
            wine_score
        )
        
        match_reasons, concerns = self._generate_feedback(
            restaurant, 
            dietary_score, 
            cuisine_score, 
            budget_score, 
            location_score, 
            wine_score
        )
        
        explanation = self._generate_explanation(restaurant, total_score, match_reasons, concerns)
        
        return EvaluationScore(
            total_score=round(total_score, 1),
            dietary_score=round(dietary_score, 1),
            cuisine_score=round(cuisine_score, 1),
            budget_score=round(budget_score, 1),
            location_score=round(location_score, 1),
            wine_score=round(wine_score, 1),
            explanation=explanation,
            match_reasons=match_reasons,
            concerns=concerns
        )
    
    def _score_dietary_fit(self, restaurant: RestaurantInfo) -> float:
        """Score dietary compatibility (0-25 points)"""
        score = 0.0
        
        if self.context.dietary.is_vegetarian:
            # Check for vegetarian options
            if restaurant.has_vegetarian_menu:
                score += 10
            
            # Score based on number of vegetarian options
            if restaurant.vegetarian_options_count >= 5:
                score += 10
            elif restaurant.vegetarian_options_count >= 3:
                score += 7
            elif restaurant.vegetarian_options_count >= 1:
                score += 4
            
            # Check menu items for quality vegetarian options
            quality_veg_keywords = ["tofu", "tempeh", "quinoa", "lentil", "chickpea", 
                                   "mushroom", "eggplant", "cauliflower", "paneer"]
            
            menu_text = " ".join(restaurant.menu_items).lower()
            quality_matches = sum(1 for keyword in quality_veg_keywords if keyword in menu_text)
            
            if quality_matches >= 3:
                score += 5
            elif quality_matches >= 1:
                score += 3
            
            # Penalty for steakhouse or seafood-focused
            if any(word in restaurant.name.lower() for word in ["steakhouse", "bbq", "seafood"]):
                score = max(0, score - 10)
        
        # Check for allergen concerns
        if self.context.dietary.allergies:
            allergen_found = False
            for allergen in self.context.dietary.allergies:
                if allergen.lower() in menu_text:
                    allergen_found = True
            
            if not allergen_found:
                score = min(25, score + 2)
        
        return min(25, score)
    
    def _score_cuisine_fit(self, restaurant: RestaurantInfo) -> float:
        """Score cuisine match (0-20 points)"""
        score = 0.0
        
        restaurant_cuisines = [c.lower() for c in restaurant.cuisine_type]
        preferred_cuisines = [c.lower() for c in self.context.cuisine.preferred_cuisines]
        
        # Direct match with preferred cuisines
        for cuisine in restaurant_cuisines:
            if cuisine in preferred_cuisines:
                score += 15
                break
            # Partial matches for asian cuisines
            elif cuisine in ["chinese", "japanese", "thai", "vietnamese", "korean", "indian"] and "asian" in preferred_cuisines:
                score += 12
                break
        
        # Bonus for fusion or variety
        if len(restaurant_cuisines) > 1:
            score += 3
        
        # Check for cuisines to avoid
        for avoid in self.context.cuisine.avoid_cuisines:
            if avoid.lower() in restaurant_cuisines:
                score = max(0, score - 10)
        
        # Spice level consideration
        if self.context.dietary.spice_tolerance == "mild":
            spicy_cuisines = ["thai", "szechuan", "sichuan", "indian", "korean"]
            if any(cuisine in restaurant_cuisines for cuisine in spicy_cuisines):
                # Check if they mention mild options
                if restaurant.reviews_summary and "mild" in restaurant.reviews_summary.lower():
                    score = max(0, score - 2)
                else:
                    score = max(0, score - 5)
        
        return min(20, score)
    
    def _score_budget_fit(self, restaurant: RestaurantInfo) -> float:
        """Score budget compatibility (0-20 points)"""
        score = 20.0
        
        # Map price symbols to estimated per-dish costs
        price_mapping = {
            "$": 15,
            "$$": 30,
            "$$$": 50,
            "$$$$": 80
        }
        
        if restaurant.price_range in price_mapping:
            avg_price = price_mapping[restaurant.price_range]
            
            # Perfect match
            if self.context.budget.min_price_per_dish <= avg_price <= self.context.budget.max_price_per_dish:
                score = 20
            # Slightly under budget (still good)
            elif avg_price < self.context.budget.min_price_per_dish:
                diff_ratio = (self.context.budget.min_price_per_dish - avg_price) / self.context.budget.min_price_per_dish
                score = 20 - (diff_ratio * 10)
            # Over budget
            else:
                diff_ratio = (avg_price - self.context.budget.max_price_per_dish) / self.context.budget.max_price_per_dish
                score = max(0, 20 - (diff_ratio * 20))
        
        return max(0, score)
    
    def _score_location_fit(self, restaurant: RestaurantInfo) -> float:
        """Score location and accessibility (0-20 points)"""
        score = 0.0
        
        # Distance scoring
        if restaurant.distance_miles is not None:
            if restaurant.distance_miles <= 1:
                score += 10
            elif restaurant.distance_miles <= 3:
                score += 8
            elif restaurant.distance_miles <= self.context.location.max_distance_miles:
                score += 5
            else:
                score += 0
        else:
            # If distance unknown, give partial credit if in same city
            if self.context.location.city.lower() in restaurant.address.lower():
                score += 5
        
        # Public transit accessibility
        if self.context.location.prefers_public_transit:
            if restaurant.near_public_transit:
                score += 10
            elif restaurant.near_public_transit is None:
                # Unknown, give partial credit
                score += 5
        else:
            score += 10  # Full points if transit not a requirement
        
        return min(20, score)
    
    def _score_wine_fit(self, restaurant: RestaurantInfo) -> float:
        """Score wine program and corkage (0-15 points)"""
        score = 0.0
        
        if self.context.restaurant.wine_list_important:
            if restaurant.wine_list_quality == "excellent":
                score += 8
            elif restaurant.wine_list_quality == "good":
                score += 6
            elif restaurant.wine_list_quality == "basic":
                score += 3
            elif restaurant.wine_list_quality is None:
                # Unknown, give partial credit
                score += 4
        else:
            score += 8  # Full points if wine not important
        
        if self.context.restaurant.corkage_preferred:
            if restaurant.allows_corkage:
                score += 7
            elif restaurant.allows_corkage is None:
                # Unknown, give partial credit
                score += 3.5
        else:
            score += 7  # Full points if corkage not important
        
        return min(15, score)
    
    def _generate_feedback(self, restaurant: RestaurantInfo, dietary: float, 
                          cuisine: float, budget: float, location: float, 
                          wine: float) -> Tuple[List[str], List[str]]:
        """Generate lists of positive matches and concerns"""
        match_reasons = []
        concerns = []
        
        # Dietary feedback
        if dietary >= 20:
            match_reasons.append("Excellent vegetarian options available")
        elif dietary >= 15:
            match_reasons.append("Good vegetarian selection")
        elif dietary < 10:
            concerns.append("Limited vegetarian options")
        
        # Cuisine feedback
        if cuisine >= 15:
            match_reasons.append(f"Serves your preferred {', '.join(restaurant.cuisine_type)} cuisine")
        elif cuisine < 10:
            concerns.append("Cuisine type doesn't match preferences")
        
        # Budget feedback
        if budget >= 18:
            match_reasons.append("Price range perfectly matches your budget")
        elif budget >= 15:
            match_reasons.append("Within budget range")
        elif budget < 10:
            concerns.append("May be outside your preferred price range")
        
        # Location feedback
        if location >= 18:
            match_reasons.append("Conveniently located with transit access")
        elif location >= 15:
            match_reasons.append("Reasonably accessible location")
        elif location < 10:
            concerns.append("Location may be inconvenient")
        
        # Wine feedback
        if wine >= 13:
            match_reasons.append("Great wine program with corkage option")
        elif wine >= 10:
            match_reasons.append("Good wine selection")
        
        return match_reasons, concerns
    
    def _generate_explanation(self, restaurant: RestaurantInfo, total_score: float,
                            match_reasons: List[str], concerns: List[str]) -> str:
        """Generate a natural language explanation of the score"""
        if total_score >= 85:
            verdict = "This is an excellent match for your preferences!"
        elif total_score >= 70:
            verdict = "This restaurant is a good fit with some minor considerations."
        elif total_score >= 50:
            verdict = "This restaurant partially matches your preferences."
        else:
            verdict = "This restaurant may not be the best fit for your preferences."
        
        explanation_parts = [verdict]
        
        if match_reasons:
            explanation_parts.append("Strengths: " + "; ".join(match_reasons) + ".")
        
        if concerns:
            explanation_parts.append("Considerations: " + "; ".join(concerns) + ".")
        
        return " ".join(explanation_parts)