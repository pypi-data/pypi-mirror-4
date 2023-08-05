__author__ = 'ajumell'


def request_details(request):
    return {
        'current_path': request.get_full_path(),
        'current_domain': request.get_host(),
        'is_https': request.is_secure(),
        'is_ajax': request.is_ajax(),
        'current_full_url': "%s%s" % (request.get_host(), request.get_full_path())
    }
