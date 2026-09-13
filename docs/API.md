# TruePass API

Run locally with:

```bash
truepass run --host 127.0.0.1 --port 8000
```

OpenAPI is available at `/docs`. Core endpoint groups implemented in Phase 23 are `/health`, `/metrics`, `/events`, `/incidents`, `/sensors`, `/timeline`, `/correlation`, `/evidence`, `/baselines`, `/similarity`, `/system`, and `/dashboard/summary`.

`create_app(..., api_key="...")` enables the API-key authentication hook through the `X-TruePass-API-Key` header. When no key is supplied, local development remains open by default. Production deployments should place the service behind TLS and configure authentication at the application and/or reverse-proxy layer.
