"""
Define your rules in one of two ways:
 - As a callable class - if you have rules that share functionality
 - as a standalone method

class CanMakePizza(object):
    # Example standalone class
    def __call__(self, topping_list, pizza_place):
        for t in topping_list:
            if t not in pizza_place.inventory_list:
                return False
        return True

can_make_pizza = CanMakePizza
rules.register('can_make_pizza', can_make_pizza)
    
def can_eat_pizza(person, topping_list):
    for t in topping_list:
        if t in person.dislike_list:
            return False
    return True
rules.register('can_eat_pizza', can_eat_pizza)

"""
import logical_rules

def evaluate_expression(exp):
    return exp
logical_rules.site.register('evaluate_expression', evaluate_expression)

def user_is_authenticated(user):
    """
        Added to the rule set automatically as an alternative to the
        login_required decorator
    """
    return user.is_authenticated()
logical_rules.site.register('user_is_authenticated', user_is_authenticated)
