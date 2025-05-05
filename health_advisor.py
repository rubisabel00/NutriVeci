class HealthAdvisor:
    def __init__(self):
        self.tips = [
            "Asegúrate de beber suficiente agua durante el día 💧",
            "Incluye vegetales de diferentes colores en tus comidas 🥗",
            "Limita el consumo de alimentos procesados 🚫",
            "Intenta comer más proteínas magras 🥩",
            "No olvides incluir frutas frescas en tu dieta 🍎",
            "Prioriza granos enteros sobre refinados 🌾",
            "Mantén un horario regular de comidas ⏰",
            "Controla el tamaño de las porciones 🍽️"
        ]
    
    def get_advice(self):
        from random import choice
        return choice(self.tips)