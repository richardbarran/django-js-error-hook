function djangoJSErrorHookGetCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function djangoJSErrorHookLogError(data) {
    var xhr = new XMLHttpRequest();

    xhr.open("POST", djangoJSErrorHandlerUrl, true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    var cookie = djangoJSErrorHookGetCookie('csrftoken');
    if (cookie) {
        xhr.setRequestHeader("X-CSRFToken", cookie);
    }
    var query = [];
    data['user_agent'] = navigator.userAgent;
    data['href'] = window.location.href;
    for (var key in data) {
        query.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
    }
    xhr.send(query.join('&'));
}

(function () {

    window.onerror = function (msg,
                               url,
                               line_number,
                               column_number,
                               error_obj) {
        var log_dict = {
            'msg': msg,
            'url': url,
            'line_number': line_number,
        }
        if (column_number) {
            log_dict['column_number'] = column_number;
        }
        if (error_obj && error_obj.stack) {
            log_dict['stack'] = error_obj.stack;
        }
        djangoJSErrorHookLogError(log_dict);
    };

    if (window.addEventListener) {
        window.addEventListener('unhandledrejection', function (rejection) {
            var log_dict = {
                'rejection_type': rejection.type
            }
            if (rejection.reason) {
                if (rejection.reason.message) {
                    log_dict['reason_message'] = rejection.reason.message;
                } else {
                    log_dict['rejection_reason'] = JSON.stringify(rejection.reason);
                }
                if (rejection.reason.stack) {
                    log_dict['reason_stack'] = rejection.reason.stack;
                }
            }
            djangoJSErrorHookLogError(log_dict);
        })
    }
})();
