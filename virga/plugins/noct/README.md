# Noct authentication plugin

Virga enables applications to check the user's authentication state before allowing access to any given route.

It does not handle logging in, only verifying that a Request is already logged in.

To add authentication to any route, import and add the `get_current_user` function as a route dependency. You also need
to supply 4 environment variables to your application at runtime to ensure it can properly parse authentication tokens.
The last 3 are identical to what they should be on the cluster with which you want users to authenticate.

- `NOCT_HOST`: the URL to which to send authentication requests. ie: <https://try.indico.io/auth>
- `ATMOSPHERE_COOKIE_SECRET`
- `ATMOSPHERE_TOKEN_SECRET`
- `ATMOSPHERE_AUTH_COOKIE_DOMAIN`

## Function

This plugin sits as a route dependency and reads, decrypts, parses, and refreshes any authentication tokens present on a Request.

Authentication depends on the presence of an auth cookie issued by IPA / Noct at login, as well as an optional refresh token used for
refreshing a user's expired session and reissue a new authentication token.

The authentication flow looks like this:

```mermaid
%%{init: { "flowchart": { "curve": "linear" } } }%%
flowchart TD
    A([CAN THE USER ACCESS\n]) --> B
    B{{Is there an auth or refresh token cookie\nin the Request?}} -->|Yes| C
    B -->|No| N
    C{{"Can I decrypt the auth token and\nis it valid (JWT not expired)?"}} -->|Yes| Y
    C -->|No| D
    D{{Is there a refresh token?}} -->|Yes|E
    D -->|No| N
    E{{"Can I decrypt it and\nis it valid (JWT not expired)?"}} -->|Yes| F
    E -->|No| N
    F[["POST /users/refresh_token\n(using token as Bearer)"]] -->|HTTP 401| N
    F -->|HTTP 200| G
    G[[Set returned auth token\nas encrypted cookie]] --> Y

    Y((ALLOW))
    N((DENY))

    style A fill:#226666
    style Y fill:#2D882D
    style N fill:#AA3838
```
