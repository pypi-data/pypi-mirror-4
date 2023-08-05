def before_scenario(context, scenario):
    # Seed empty HTTP headers so steps do not need to check and create.
    context.headers = {}

    # Seed empty Jinja2 template data so steps do not need to check and create.
    context.template_data = {}

    # Default repeat attempt counts and delay for polling GET.
    context.n_attempts = 20
    context.pause_between_attempts = 0.1

    # No authentication by default.
    context.auth = None
