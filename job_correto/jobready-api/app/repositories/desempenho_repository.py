from sqlalchemy import func

from app.extensions import db
from app.models.entrevista import Entrevista
from app.models.pergunta import Pergunta
from app.models.resposta import Resposta


class DesempenhoRepository:

    NOTA_MINIMA_ADEQUADA = 6.0
    TAMANHO_MINIMO_SEQUENCIA = 3

    DESVIO_CONSISTENTE = 1.0
    DESVIO_MODERADO = 2.0
    MINIMO_TENTATIVAS_CONSISTENCIA = 3

    @staticmethod
    def calcular_estatisticas_desempenho_usuario(usuario_id: int) -> dict:
        nota = Resposta.nota_ia
        total, media, maior, menor, media_quadrados = (
            db.session.query(
                func.count(nota),
                func.avg(nota),
                func.max(nota),
                func.min(nota),
                func.avg(nota * nota),
            )
            .join(Entrevista, Resposta.entrevista_id == Entrevista.id)
            .filter(Entrevista.usuario_id == usuario_id, nota.isnot(None))
            .one()
        )

        if not total:
            return {
                "total_tentativas": 0,
                "media_notas": None,
                "maior_nota": None,
                "menor_nota": None,
                "amplitude": None,
                "status_consistencia": "sem_dados",
            }

        amplitude = round(maior - menor, 2)
        variancia = max(0.0, media_quadrados - media ** 2)
        desvio = variancia ** 0.5

        return {
            "total_tentativas": int(total),
            "media_notas": round(media, 2),
            "maior_nota": round(maior, 2),
            "menor_nota": round(menor, 2),
            "amplitude": amplitude,
            "status_consistencia": DesempenhoRepository._classificar_consistencia(
                int(total), desvio
            ),
        }

    @staticmethod
    def _classificar_consistencia(total: int, desvio: float) -> str:
        if total < DesempenhoRepository.MINIMO_TENTATIVAS_CONSISTENCIA:
            return "dados_insuficientes"
        if desvio <= DesempenhoRepository.DESVIO_CONSISTENTE:
            return "consistente"
        if desvio <= DesempenhoRepository.DESVIO_MODERADO:
            return "moderado"
        return "inconsistente"

    @staticmethod
    def detectar_gargalos_sequenciais(usuario_id: int) -> list:
        historico = (
            db.session.query(Pergunta.categoria, Resposta.nota_ia)
            .select_from(Resposta)
            .join(Entrevista, Resposta.entrevista_id == Entrevista.id)
            .join(Pergunta, Resposta.pergunta_id == Pergunta.id)
            .filter(Entrevista.usuario_id == usuario_id, Resposta.nota_ia.isnot(None))
            .order_by(Resposta.respondido_em.asc(), Resposta.id.asc())
            .all()
        )

        limite = DesempenhoRepository.NOTA_MINIMA_ADEQUADA
        minimo = DesempenhoRepository.TAMANHO_MINIMO_SEQUENCIA

        corrente = {}
        melhor = {}

        for categoria, nota in historico:
            if nota < limite:
                corrente.setdefault(categoria, []).append(nota)
                atual = corrente[categoria]
                if len(atual) >= minimo and len(atual) >= len(melhor.get(categoria, [])):
                    melhor[categoria] = list(atual)
            else:
                corrente[categoria] = []

        gargalos = [
            {
                "categoria": categoria,
                "maior_sequencia_baixa": len(notas),
                "media_na_sequencia": round(sum(notas) / len(notas), 2),
                "em_andamento": len(corrente.get(categoria, [])) >= minimo,
            }
            for categoria, notas in melhor.items()
        ]
        gargalos.sort(key=lambda g: (-g["maior_sequencia_baixa"], g["media_na_sequencia"]))
        return gargalos
