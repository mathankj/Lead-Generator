"""Test script to verify Apollo and Hunter API keys."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")


async def test_apollo():
    """Test Apollo API connection."""
    print("\n=== Testing Apollo.io API ===")

    if not APOLLO_API_KEY:
        print("❌ APOLLO_API_KEY not found in .env")
        return False

    try:
        import httpx

        url = "https://api.apollo.io/api/v1/mixed_companies/search"
        payload = {
            "api_key": APOLLO_API_KEY,
            "q_organization_keyword_tags": ["AI", "artificial intelligence"],
            "page": 1,
            "per_page": 5,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                total = data.get("pagination", {}).get("total_entries", 0)
                orgs = len(data.get("organizations", []))
                print(f"✅ Apollo API working! Found {orgs} companies (total: {total})")

                # Show first result
                if data.get("organizations"):
                    org = data["organizations"][0]
                    print(f"   Sample: {org.get('name')} - {org.get('primary_domain')}")

                return True
            elif response.status_code == 401:
                print(f"❌ Apollo API: Invalid API key")
                return False
            elif response.status_code == 429:
                print(f"⚠️  Apollo API: Rate limit exceeded")
                return False
            else:
                print(f"❌ Apollo API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Apollo API error: {str(e)}")
        return False


async def test_hunter():
    """Test Hunter API connection."""
    print("\n=== Testing Hunter.io API ===")

    if not HUNTER_API_KEY:
        print("❌ HUNTER_API_KEY not found in .env")
        return False

    try:
        import httpx

        # Test with account endpoint to verify key
        url = "https://api.hunter.io/v2/account"
        params = {"api_key": HUNTER_API_KEY}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                account = data.get("data", {})
                email = account.get("email", "N/A")
                plan = account.get("plan_name", "N/A")
                searches_available = account.get("requests", {}).get("searches", {}).get("available", 0)

                print(f"✅ Hunter API working!")
                print(f"   Account: {email}")
                print(f"   Plan: {plan}")
                print(f"   Searches available: {searches_available}")

                return True
            elif response.status_code == 401:
                print(f"❌ Hunter API: Invalid API key")
                return False
            elif response.status_code == 429:
                print(f"⚠️  Hunter API: Rate limit exceeded")
                return False
            else:
                print(f"❌ Hunter API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Hunter API error: {str(e)}")
        return False


async def main():
    """Run all API tests."""
    print("=" * 50)
    print("API Keys Verification Test")
    print("=" * 50)

    apollo_ok = await test_apollo()
    hunter_ok = await test_hunter()

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Apollo.io: {'✅ Working' if apollo_ok else '❌ Failed'}")
    print(f"  Hunter.io: {'✅ Working' if hunter_ok else '❌ Failed'}")
    print("=" * 50)

    if apollo_ok and hunter_ok:
        print("\n🎉 All API keys are configured correctly!")
        print("You can now start the server with: uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Please fix the API key issues above before starting the server.")
        print("\nTo get API keys:")
        print("  - Apollo: https://www.apollo.io/ → Settings → API")
        print("  - Hunter: https://hunter.io/api-keys")


if __name__ == "__main__":
    asyncio.run(main())
