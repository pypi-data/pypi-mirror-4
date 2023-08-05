from django.contrib.auth import decorators
from django.utils.decorators import method_decorator


login_required_m = method_decorator(decorators.login_required)
permission_required_m = method_decorator(decorators.permission_required)
user_passes_test_m = method_decorator(decorators.user_passes_test)
