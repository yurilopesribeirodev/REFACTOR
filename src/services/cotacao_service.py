# src/services/cotacao_service.py
import requests


class CotacaoService:
    BASE_URL = "https://brapi.dev/api/quote"

    def buscar_cotacao(self, ticker: str) -> dict | None:
        try:
            resposta = requests.get(f"{self.BASE_URL}/{ticker}", timeout=5)
            dados = resposta.json()

            if "results" not in dados or len(dados["results"]) == 0:
                return None

            resultado = dados["results"][0]
            return {
                "preco_atual": resultado["regularMarketPrice"],
                "nome": resultado["longName"],
            }
        except (requests.RequestException, KeyError):
            return None