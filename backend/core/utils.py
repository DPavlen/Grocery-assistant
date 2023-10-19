# import io
# from django.db.models import Sum
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.pdfgen import canvas
# from recipes.models import Ingredient, CompositionOfDish


# def create_shopping_list_report(shopping_cart):
#     """Реализует только создание PDF-документа в буфере.
#     А в download_shopping_cart происходит использование буфера."""
#     pdf_filename = 'shopping_cart.pdf'
#     buffer = io.BytesIO()

#     # Загрузка шрифта
#     pdfmetrics.registerFont(TTFont('Arial', '/core/'Arial.ttf'))

#     pdf = canvas.Canvas(buffer)

#     y = 800

#     recipes = shopping_cart.values_list('recipe_id', flat=True)
#     buy_list = CompositionOfDish.objects.filter(
#         recipe__in=recipes
#     ).values(
#         'ingredient'
#     ).annotate(
#         amount=Sum('amount')
#     )

#     buy_list_text = f'Foodgram Список покупок: \n'
#     for item in buy_list:
#         ingredient = Ingredient.objects.get(pk=item['ingredient'])
#         amount = item['amount']
#         buy_list_text += (
#             f'{ingredient.name}, {amount} '
#             f'{ingredient.measurement_unit} \n'
#         )

#     # Рисование строки с использованием шрифта Arial
#     pdf.setFont('Arial', 14)
    
#     # Разделение текста на строки с автоматическим переносом
#     lines = buy_list_text.split('\n')
#     for line in lines:
#         pdf.drawString(100, y, line)
#         y -= 20
    
#     y -= 20
#     pdf.showPage()
#     pdf.save()
#     buffer.seek(0)
#     return buffer.getvalue()



