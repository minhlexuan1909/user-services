from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        print("renderer_context", renderer_context)
        status_code = renderer_context["response"].status_code
        request = renderer_context.pop("request")
        # page = request.query_params.get("page", None)
        response = {
            "status": status_code,
            "data": data,
        }

        return super(CustomJSONRenderer, self).render(
            response, accepted_media_type, renderer_context
        )
