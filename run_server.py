import os
import uvicorn

def main():
    # Garantir que a porta seja um inteiro
    port = int(os.getenv("PORT", "8000"))
    
    # Iniciar o servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
