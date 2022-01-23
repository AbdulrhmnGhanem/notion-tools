import click


def positive_num(ctx, param, value):
    if value < 1:
        raise click.BadParameter("Should be a positive integer!")
    return value
