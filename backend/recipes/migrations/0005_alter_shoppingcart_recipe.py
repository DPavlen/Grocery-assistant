# Generated by Django 3.2 on 2023-10-16 23:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0004_alter_shoppingcart_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shoppingcart",
                to="recipes.recipe",
                verbose_name="Рецепты пользователей",
            ),
        ),
    ]
