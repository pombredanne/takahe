import base64
from typing import List, TypedDict

from cryptography.hazmat.primitives import hashes
from django.http import HttpRequest


class HttpSignature:
    """
    Allows for calculation and verification of HTTP signatures
    """

    @classmethod
    def calculate_digest(cls, data, algorithm="sha-256") -> str:
        """
        Calculates the digest header value for a given HTTP body
        """
        if algorithm == "sha-256":
            digest = hashes.Hash(hashes.SHA256())
            digest.update(data)
            return "SHA-256=" + base64.b64encode(digest.finalize()).decode("ascii")
        else:
            raise ValueError(f"Unknown digest algorithm {algorithm}")

    @classmethod
    def headers_from_request(cls, request: HttpRequest, header_names: List[str]) -> str:
        """
        Creates the to-be-signed header payload from a Django request"""
        headers = {}
        for header_name in header_names:
            if header_name == "(request-target)":
                value = f"post {request.path}"
            elif header_name == "content-type":
                value = request.META["CONTENT_TYPE"]
            else:
                value = request.META[f"HTTP_{header_name.upper()}"]
            headers[header_name] = value
        return "\n".join(f"{name.lower()}: {value}" for name, value in headers.items())

    @classmethod
    def parse_signature(cls, signature) -> "SignatureDetails":
        bits = {}
        for item in signature.split(","):
            name, value = item.split("=", 1)
            value = value.strip('"')
            bits[name.lower()] = value
        signature_details: SignatureDetails = {
            "headers": bits["headers"].split(),
            "signature": base64.b64decode(bits["signature"]),
            "algorithm": bits["algorithm"],
            "keyid": bits["keyid"],
        }
        return signature_details


class SignatureDetails(TypedDict):
    algorithm: str
    headers: List[str]
    signature: bytes
    keyid: str
