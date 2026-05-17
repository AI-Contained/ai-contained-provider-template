"""TrustClient — performs key exchange with a trust server daemon."""

import httpx
import nacl.public
import nacl.signing


class TrustClient:
    """Generates ephemeral keypairs and registers with a trust server.

    Keypairs are generated once at instantiation and held in memory only —
    never written to disk, never passed to subprocesses.

    - Ed25519 SigningKey: signs outgoing requests (authentication)
    - Curve25519 PrivateKey: decrypts incoming responses (confidentiality)
    """

    def __init__(self, target: httpx.URL | httpx.Client) -> None:
        # In production pass httpx.URL — client is created internally.
        # In tests pass a TestClient (starlette.testclient.TestClient is a subclass of httpx.Client).
        if isinstance(target, httpx.URL):
            self._http = httpx.Client(base_url=str(target))
        else:
            self._http = target
        self._signing_key = nacl.signing.SigningKey.generate()
        self._private_key = nacl.public.PrivateKey.generate()

    def register(self) -> bool:
        """POST public keys to /trust/register.

        Returns:
            True  — successfully registered (HTTP 200)
            False — already registered from this IP (HTTP 401)

        Raises:
            httpx.HTTPStatusError: unexpected response — indicates misconfiguration.
                                   Includes server URL and response body for debugging.
        """
        response = self._http.post(
            "/trust/register",
            json={
                "signing_public_key": self._signing_key.verify_key.encode().hex(),
                "encryption_public_key": bytes(self._private_key.public_key).hex(),
            },
        )
        if response.status_code == 200:
            return True
        if response.status_code == 401:
            return False
        response.raise_for_status()
        raise RuntimeError("unreachable")
