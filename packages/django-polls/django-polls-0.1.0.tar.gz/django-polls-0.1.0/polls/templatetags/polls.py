from django import template


register = template.Library()


@register.simple_tag
def user_can_vote(poll, user):
    return poll.can_vote(user)
