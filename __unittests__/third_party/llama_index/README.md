LlamaIndex classes rely on openai on many default settings. While the tests themselves
dont actually use openai, the key is needed to avoid a lot of configuration

create a .env file and put in your open ai key like

```
OPENAI_API_KEY=your_key_here
```