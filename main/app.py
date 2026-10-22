from main.main import initialize_api_with_dependencies
import nest_asyncio

nest_asyncio.apply()

app = initialize_api_with_dependencies()
