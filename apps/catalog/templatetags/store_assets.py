from django import template

register = template.Library()


@register.filter
def store_asset(slug, prefix):
    return f"img/store/{prefix}-{slug}.webp"
