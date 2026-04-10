def choose_fetch_mode(status_code: int) -> str:
    return "browser" if status_code == 403 else "http"
