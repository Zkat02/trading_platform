from orders.exceptions import OrderDoNotCreated


def check_user_balance(user, user_action_type, stock, quantity):
    if user_action_type == "buy":
        if user.balance >= quantity * stock.price_per_unit_sail:
            return True
        raise OrderDoNotCreated("Insufficient balance.")
    elif user_action_type == "sell":
        return True
    raise OrderDoNotCreated('Field user_action_type is not "buy" or "sell".')


def calculate_user_balance(user, user_action_type, stock, quantity):
    if user_action_type == "buy":
        if user.balance >= quantity * stock.price_per_unit_sail:
            user.balance -= quantity * stock.price_per_unit_sail
        else:
            raise OrderDoNotCreated("Insufficient balance.")
    elif user_action_type == "sell":
        user.balance += quantity * stock.price_per_unit_buy
    else:
        raise OrderDoNotCreated('Field user_action_type is not "buy" or "sell".')
    user.save()
    return user.balance


def close_order(order):
    order.status = "closed"
    order.save()

    user = order.user
    stock = order.stock
    balance = calculate_user_balance(user, order.user_action_type, stock, order.quantity)
    return balance
