from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from attrs import define
from dotenv import load_dotenv
import os
from rest_framework.views import APIView
from random import SystemRandom
from urllib.parse import urlencode
from django.urls import reverse_lazy
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
import requests
import jwt
from typing import Dict, Any
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


load_dotenv()

@define
class GoogleRawLoginCredentials:
    """
    Represents the Google OAuth2 client credentials 
    required for the login flow.

    Attributes:
        client_id (str): The client ID for Google OAuth2.
        client_secret (str): The client secret for Google OAuth2.
    """
    client_id: str
    client_secret: str

@define
class GoogleAccessTokens:
    """
    Represents the Google OAuth2 access tokens.

    Attributes:
        id_token (str): The ID token.
        access_token (str): The access token.

    Methods:
        decode_id_token(client_id: str) -> Dict[str, str]: 
        Decode the ID token using the provided client ID.
    """
    id_token: str
    access_token: str

    def decode_id_token(self, client_id: str) -> Dict[str, str]:
        """
        Decode the provided ID token using JWT with the 
        specified client ID as the audience.

        Args:
            client_id (str): The client ID to verify the 
            audience of the token.

        Returns:
            Dict[str, str]: Decoded token information.

        Raises:
            ValueError: If the audience in the token is invalid.
        """
        id_token = self.id_token
        try:
            return jwt.decode(
                jwt=id_token, audience=client_id,
                options={"verify_signature": False})
        except jwt.InvalidAudienceError as e:
            raise ValueError("Invalid audience.") from e

def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    """
    Retrieve Google OAuth2 client credentials from environment variables.

    Returns:
        GoogleRawLoginCredentials: Object containing the client ID and client secret.
    
    Raises:
        ImproperlyConfigured: If the required environment variables are missing.
    """
    client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
  
    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    return GoogleRawLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )



class GoogleRawLoginFlowService:
    """
    Service class for handling the Google OAuth2 login flow.

    Attributes:
        API_URI: The URI for the Google OAuth2 API.
        GOOGLE_AUTH_URL: The URL for Google OAuth2 authorization.
        GOOGLE_ACCESS_TOKEN_OBTAIN_URL: The URL for obtaining Google access tokens.
        GOOGLE_USER_INFO_URL: The URL for retrieving user information from Google.
        SCOPES: List of scopes for Google OAuth2.
    """

    API_URI = reverse_lazy("google_auth2")

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_raw_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        """
        Generate a random state session token of a specified length using the given character set.

        Args:
            length (int): The length of the token to generate.
            chars (Iterable): The character set to use for token generation.

        Returns:
            str: A randomly generated state session token.
        """        
        # This is how it's implemented in the official SDK
        rand = SystemRandom()
        return "".join(rand.choice(chars) for _ in range(length))

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        return 'http://localhost:8000/api/google-oauth2/login/raw/callback/'

    def get_authorization_url(self):
        """
        Generate the Google OAuth2 authorization URL 
        and a unique state token.

        Returns:
            Tuple[str, str]: A tuple containing the authorization 
            URL and the generated state token.
        """

        redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"
        return authorization_url, state
    
    def get_tokens(self, *, code: str):
        """
        Obtain Google access tokens using the provided authorization code.

        Args:
            code (str): The authorization code received from Google.

        Returns:
            GoogleAccessTokens: Object containing the obtained Google access tokens.

        Raises:
            ValueError: If access token retrieval from Google fails.
        """

        redirect_uri = self._get_redirect_uri()

        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ValueError("Failed to obtain access token from Google.")

        tokens = response.json()
        return GoogleAccessTokens(
            id_token=tokens["id_token"], access_token=tokens["access_token"]
        )
    
    def get_user_info(self, *, google_tokens: GoogleAccessTokens) -> Dict[str, Any]:
        """
        Retrieve user information from Google using the
        provided Google access tokens.

        Args:
            google_tokens (GoogleAccessTokens): Object 
            containing Google access tokens.

        Returns:
            Dict[str, Any]: User information retrieved from Google.
        
        Raises:
            ValueError: If user info retrieval from Google fails.
        """

        access_token = google_tokens.access_token
        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
        response = requests.get(self.GOOGLE_USER_INFO_URL, params={"access_token": access_token})

        if not response.ok:
            raise ValueError("Failed to obtain user info from Google.")

        return response.json()

def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    refresh_token = token_data
    return refresh_token.access_token, refresh_token