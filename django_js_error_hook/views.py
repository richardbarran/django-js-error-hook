from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import logging

ERROR_ID = getattr(settings, 'JAVASCRIPT_ERROR_ID', 'javascript_error')
CSRF_EXEMPT = getattr(settings, 'JAVASCRIPT_ERROR_CSRF_EXEMPT', False)

logger = logging.getLogger(ERROR_ID)


class JSErrorHandlerView(View):
    """View that take the JS error as POST parameters and log it"""

    def post(self, request):
        """Read POST data and log it as an JS error"""
        error_dict = request.POST.dict()

        user_agent = error_dict.get('user_agent', '')

        if 'msg' in error_dict:
            msg = f"JS error: {error_dict['msg']}"
            # Not all keys are provided (depending on the browser) so set default values.
            url = error_dict.get('url', '')
            line_number = error_dict.get('line_number', '')
            column_number = error_dict.get('column_number', '')
            stack = error_dict.get('stack', '')
            # formatted_details is a string ready for use as email body.
            formatted_details = f'{url}\nline {line_number}'
            if column_number:
                formatted_details += f': col {column_number}'
            if stack:
                formatted_details += f'\n{stack}'
            formatted_details += f'\n{user_agent}'
            extra_data = {
                'url': url,
                'line_number': line_number,
                'column_number': column_number,
                'stack': stack,
                'user_agent': user_agent,
                'formatted_details': formatted_details
            }
        else:
            msg = f"JS unhandledrejection: {error_dict['rejection_type']}"
            # Not all keys are provided (depending on the browser) so set default values.
            reason_message = error_dict.get('reason_message', '')
            rejection_reason = error_dict.get('rejection_reason', '')
            reason_stack = error_dict.get('reason_stack', '')
            # formatted_details is a string ready for use as email body.
            formatted_details = ''
            if reason_message:
                formatted_details += f'\nreason_message: {reason_message}'
            if rejection_reason:
                formatted_details += f'\nreason_message: {rejection_reason}'
            if reason_stack:
                formatted_details += f'\nreason_message: {reason_stack}'
            formatted_details += f'\n{user_agent}'
            extra_data = {
                'reason_message': reason_message,
                'rejection_reason': rejection_reason,
                'reason_stack': reason_stack,
                'formatted_details': formatted_details
            }

        # Add the logged-in user (if applicable).
        if hasattr(request, 'user') and request.user.is_authenticated:
            extra_data['user'] = request.user

        logger.log(
            logging.ERROR,
            msg,
            extra=extra_data
        )
        return HttpResponse('Error logged')


if CSRF_EXEMPT:
    js_error_view = csrf_exempt(JSErrorHandlerView.as_view())
else:
    js_error_view = JSErrorHandlerView.as_view()
