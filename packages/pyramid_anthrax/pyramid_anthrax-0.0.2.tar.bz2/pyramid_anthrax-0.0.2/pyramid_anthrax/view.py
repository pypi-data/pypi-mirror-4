import sys
from decorator import decorator

import pyramid

def _get_request(args):
    return args[1] if len(args) == 2 else args[0]

def form_renderer(
    Form=None, get_form_factory=None, form_mode=None, action=None
):
    def form_renderer_(view, *view_args):
        request = _get_request(view_args)
        if Form:
            form = Form(mode=form_mode, action=action)
        elif get_form_factory:
            form = get_form_factory(*view_args)(mode=form_mode, action=action)
        if request.method == 'POST':
            form.__raw__ = request.POST
        request.form = form
        return view(*view_args)
    return decorator(form_renderer_)


def form_post(
    Form=None, get_form_factory=None, on_invalid=None, form_mode=None, 
    action=None
):
    def form_post_(view, *view_args):
        request = _get_request(view_args)
        if Form:
            form = Form(mode=form_mode, action=action)
        elif get_form_factory:
            form = get_form_factory(*view_args)(mode=form_mode, action=action)
        form.kwargs['method'] = 'POST'
        form.__raw__ = request.POST
        request.form = form
        if not form.__valid__ and on_invalid is not None:
            return pyramid.view.render_view_to_response(
                context=request.context, request=request, name=on_invalid)
        else: 
            return view(*view_args)
    return decorator(form_post_)
