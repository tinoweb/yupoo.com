import os
import uvicorn

if __name__ == "__main__":
    # Obter a porta do ambiente
    port = int(os.getenv("PORT", "8000"))
    
    # Configurar o uvicorn
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        workers=4,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
    
    # Iniciar o servidor
    server = uvicorn.Server(config)
    server.run()
