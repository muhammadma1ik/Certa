from dotenv import load_dotenv
import os


def mask_value(value: str, visible: int = 8) -> str:
    if len(value) <= visible:
        return "***"

    return f"{value[:visible]}...***"


def main():
    load_dotenv()

    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT")

    if not endpoint:
        raise ValueError("Missing AZURE_AI_PROJECT_ENDPOINT in .env")

    if not deployment:
        raise ValueError("Missing AZURE_AI_MODEL_DEPLOYMENT in .env")

    print("Foundry configuration loaded successfully.")
    print(f"Project endpoint: {mask_value(endpoint)}")
    print(f"Model deployment: {deployment}")


if __name__ == "__main__":
    main()
