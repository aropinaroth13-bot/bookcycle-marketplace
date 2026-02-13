"""
Security middleware for production
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "frame-ancestors 'none';"
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=()'
        )
        
        return response


class ForceHTTPSMiddleware(MiddlewareMixin):
    """Force HTTPS in production"""
    
    def process_request(self, request):
        if not request.is_secure() and not request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
            if request.method == 'GET':
                url = request.build_absolute_uri(request.get_full_path())
                secure_url = url.replace('http://', 'https://')
                return HttpResponsePermanentRedirect(secure_url)
        return None
