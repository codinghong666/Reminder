LLM_REGISTER = {}

def register_llm(name):
    def decorator(func):
        if func in LLM_REGISTER and LLM_REGISTER[name] != func:
            raise ValueError(f"{str(name)} already registered with different model")
        LLM_REGISTER[name] = func
        return func
    return decorator

def get_llm(name):
    if name not in LLM_REGISTER:
        raise ValueError(f"LLM {name} not found")
    return LLM_REGISTER[name]