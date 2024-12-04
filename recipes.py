from flask import Blueprint, render_template, request

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
def recipes():
    # Optionally fetch all recipes or let user input ingredients
    return render_template('recipe.html', title="Recipe Suggestions")

@recipes_bp.route('/suggest', methods=['POST'])
def suggest_recipe():
    ingredients = request.form.get('ingredients')
    # AI-powered recipe suggestion logic
    recommended_recipes = ["Example Recipe 1", "Example Recipe 2"]  # Placeholder
    return render_template('recipe.html', title="Recipe Suggestions", recommended_recipes=recommended_recipes)
