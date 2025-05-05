import pandas as pd
from recipe_recommender import RecipeRecommender

class MenuPlanner:
    def __init__(self):
        self.recommender = RecipeRecommender()
        self.days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    def generate_weekly_menu(self):
        menu = "📅 Menú Semanal:\n\n"
        for i, day in enumerate(self.days, 1):
            menu += f"{i}. {day}:\n"
            menu += f"   🍽️ {self.recommender.get_recommendation()}\n\n"
        
        menu += "\nElige un número del 1 al 7 para ver más detalles de la receta de ese día."
        return menu