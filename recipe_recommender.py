import pandas as pd
import random
import os

class RecipeRecommender:
    def __init__(self):
        try:
            file_path = 'data/recipes.csv'
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No se encontró el archivo de recetas en: {file_path}")
            self.recipes = pd.read_csv(file_path)
            
            # Definir restricciones por condición de salud
            self.health_restrictions = {
                'diabetes': ['azúcar', 'miel', 'dulce', 'caramelo', 'chocolate'],
                'hipertension': ['sal', 'salado', 'embutidos', 'conservas'],
                'celiaquia': ['trigo', 'gluten', 'harina', 'pan', 'pasta'],
                'lactosa': ['leche', 'queso', 'yogur', 'crema', 'mantequilla'],
                'alergia a mariscos': ['pescado', 'marisco', 'camarón', 'langosta', 'atún', 'salmón', 'mejillones', 'calamares'],
                'alergia a nueces': ['nuez', 'nueces', 'almendra', 'almendras', 'cacahuete', 'maní', 'avellana', 'pistacho']
            }
        except Exception as e:
            print(f"Error al cargar las recetas: {str(e)}")
            self.recipes = None
    
    def get_recommendation(self, user_profile=None):
        if self.recipes is None:
            return "Lo siento, hay un problema al acceder a las recetas. Por favor, inténtalo más tarde."
            
        try:
            available_recipes = self.recipes.copy()
            
            if user_profile and 'health_conditions' in user_profile:
                # Filtrar recetas según condiciones de salud
                for condition in user_profile['health_conditions']:
                    if condition.lower() in self.health_restrictions:
                        restricted_ingredients = self.health_restrictions[condition.lower()]
                        for ingredient in restricted_ingredients:
                            available_recipes = available_recipes[
                                ~available_recipes['Ingredients'].str.lower().str.contains(ingredient, na=False)
                            ]
            
            if len(available_recipes) == 0:
                return "Lo siento, no encontré recetas que se ajusten a tus condiciones de salud. Por favor, consulta con tu médico."
            
            recipe = available_recipes.sample(n=1).iloc[0]
            
            # Personalizar el mensaje según el perfil
            message = f"Te recomiendo: {recipe['Recipe']}\n\n"
            message += f"Esta receta es adecuada para tu perfil"
            if user_profile and 'health_conditions' in user_profile:
                message += f" teniendo en cuenta tus condiciones de salud: {', '.join(user_profile['health_conditions'])}"
            message += f"\n\nIngredientes:\n{recipe['Ingredients']}\n\n"
            message += f"Instrucciones:\n{recipe['Instructions']}\n\n"
            message += f"Calorías: {recipe['Calories']}"
            
            return message
        except Exception as e:
            return f"Lo siento, ocurrió un error al buscar la receta: {str(e)}"