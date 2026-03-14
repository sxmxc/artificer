# Admin UI

The admin UI is a React + Vite application that lets users manage mock endpoints.

## Key screens
- **Login**: Basic auth credentials.
- **Endpoint list**: Search, filter, enable/disable, duplicate, delete.
- **Endpoint editor**: Create/update an endpoint (path, method, schemas, templates, behavior).
- **Preview**: Generate a sample response and preview generated OpenAPI snippet.

## API contract
The frontend communicates with the backend via the admin API under `/api/admin`.
- `GET /api/admin/endpoints`
- `GET /api/admin/endpoints/{id}`
- `POST /api/admin/endpoints`
- `PUT /api/admin/endpoints/{id}`
- `DELETE /api/admin/endpoints/{id}`

## UX notes
- Use a JSON editor component for schema/template fields.
- Provide an "Example response" preview that calls the public mock endpoint.
- Show validation errors from the backend when saving.
